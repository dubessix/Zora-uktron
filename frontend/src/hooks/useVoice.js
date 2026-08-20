import { useRef, useState, useCallback, useEffect } from 'react';

/**
 * useVoice Hook — human-like wake-word voice (Phase 7).
 *
 * Command-catching reliability fixes:
 *  1. Mic lifecycle is managed in useEffect (start on enable, clean stop/abort
 *     on disable/unmount) — no `setTimeout` side-effects in the render body, no
 *     duplicate recognizers.
 *  2. Commands are dispatched on a short SILENCE PAUSE (~1.4s) even if the
 *     browser never marks a result `final`, so a command is never lost.
 *  3. Recognition language is configurable via VITE_VOICE_LANG (default en-IN),
 *     instead of being hardcoded to hi-IN (which mangles English/Bengali).
 *  4. Fatal errors (permission denied / not allowed) stop auto-restart instead
 *     of spinning forever.
 *  5. Wake words are matched on word boundaries to avoid false positives.
 *
 * Listening-bug fixes (2026-08-20, see voice_bugs_report.md):
 *  A. Transient errors (`network`, `audio-capture`, `no-speech`, `aborted`)
 *     are now RECOVERABLE: the hook auto-restarts with bounded backoff instead
 *     of permanently locking the mic. Only `not-allowed` stays fatal until the
 *     user re-enables voice.
 *  B. `stop()` detaches all handlers BEFORE aborting and bumps a generation
 *     counter, so an async `onend` from a stale recognizer can never restart
 *     itself or fight the current one (no duplicate recognizers).
 *  C. Restarts are deferred with `setTimeout` instead of a synchronous
 *     `rec.start()` inside `onend` (avoids Chrome InvalidStateError).
 *  D. Wake words tolerate surrounding punctuation ("ultron!", "wake up!") via
 *     a punctuation-normalized match with original-coordinate slicing.
 *  E. Long commands are no longer truncated: every final/interim chunk is
 *     accumulated and dispatched ONCE on silence (or on recognizer end), never
 *     on the first final chunk.
 *  F. The command handler is read from a ref, so the latest handler is always
 *     used even after re-renders (no stale closure).
 */
const WAKE_WORDS = [
  "ultron", "jarvis", "zora", "hey ultron", "hi ultron",
  "ok ultron", "wake up", "iron man", "activate"
];

// Recognition language: configurable, defaults to English-India which handles
// mixed English/Hinglish commands well. Override with VITE_VOICE_LANG.
const RECOG_LANG = (import.meta.env.VITE_VOICE_LANG || "en-IN");

// Send the captured command after this many ms of silence (pause in speech).
const SILENCE_FLUSH_MS = 1400;

// Errors that permanently block recognition until the user re-enables voice.
const FATAL_ERRORS = new Set(["not-allowed", "service-not-allowed"]);
// Errors that are usually transient — the mic can recover on its own.
const RECOVERABLE_ERRORS = new Set([
  "network", "audio-capture", "no-speech", "aborted",
  "language-not-supported",
]);

// Auto-restart backoff after a recoverable error (grows on repeated failures).
const RESTART_BACKOFF_MS = 1200;
const MAX_RESTART_BACKOFF_MS = 8000;

/**
 * Match a wake phrase in the transcript, tolerating punctuation around it.
 * Returns { matched: phrase|null, rest } where `rest` is the original-coordinate
 * text AFTER the wake word (so "ultron! play music" yields "play music").
 */
function matchesWakeWord(transcript) {
  const low = transcript.toLowerCase();

  // Build a punctuation-normalized copy while mapping each normalized
  // character back to its original index in the transcript.
  const origIdx = [];
  let cleaned = "";
  for (let i = 0; i < low.length; i++) {
    const ch = low[i];
    if (/[\w]/.test(ch)) {
      cleaned += ch;
    } else {
      cleaned += " ";
    }
    origIdx.push(i);
  }
  // Collapse whitespace runs, keeping the FIRST original index of each run.
  const normChars = [];
  const normMap = [];
  let prevSpace = false;
  for (let i = 0; i < cleaned.length; i++) {
    const ch = cleaned[i];
    if (ch === " ") {
      if (!prevSpace) {
        normChars.push(" ");
        normMap.push(origIdx[i]);
        prevSpace = true;
      }
    } else {
      normChars.push(ch);
      normMap.push(origIdx[i]);
      prevSpace = false;
    }
  }
  const norm = normChars.join("");

  // Match longest phrases first so "hey ultron" wins over "ultron".
  const phrases = [...WAKE_WORDS].sort((a, b) => b.length - a.length);
  for (const phrase of phrases) {
    const phraseNorm = phrase.toLowerCase();
    const idx = norm.indexOf(phraseNorm);
    if (idx < 0) continue;
    // Word boundary check (norm has single spaces, punctuation became spaces).
    const before = idx === 0 ? " " : norm[idx - 1];
    const afterIdx = idx + phraseNorm.length;
    const after = afterIdx >= norm.length ? " " : norm[afterIdx];
    if (!/\s/.test(before) || !/\s/.test(after)) continue;

    // Slice the ORIGINAL transcript after the matched phrase, then strip any
    // leading punctuation/space ("ultron!" -> rest after "ultron").
    const restStartOrig =
      normMap[afterIdx] !== undefined ? normMap[afterIdx] : transcript.length;
    const rest = transcript
      .slice(restStartOrig)
      .replace(/^[^\w]+/, "")
      .trim();
    return { matched: phrase, rest };
  }
  return { matched: null, rest: "" };
}

export default function useVoice({ onCommand, enabled }) {
  const [isListening, setIsListening] = useState(false);
  const [wakeDetected, setWakeDetected] = useState(false);
  const [heardText, setHeardText] = useState("");
  const [voiceError, setVoiceError] = useState("");
  const supported = typeof window !== 'undefined' && Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);
  const recRef = useRef(null);
  const capturingRef = useRef(false);
  const finalTextRef = useRef("");
  const silenceTimerRef = useRef(null);
  const restartTimerRef = useRef(null);
  const fatalRef = useRef(false);
  const backoffRef = useRef(RESTART_BACKOFF_MS);
  const enabledRef = useRef(enabled);
  enabledRef.current = enabled;
  // Always invoke the LATEST command handler (fixes stale-closure dispatches).
  const onCommandRef = useRef(onCommand);
  onCommandRef.current = onCommand;
  // Generation counter: only the current recognizer may act/restart itself.
  const generationRef = useRef(0);

  const clearSilenceTimer = () => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
  };

  const clearRestartTimer = () => {
    if (restartTimerRef.current) {
      clearTimeout(restartTimerRef.current);
      restartTimerRef.current = null;
    }
  };

  const dispatch = useCallback((rawCmd) => {
    let cmd = (rawCmd || "").trim();
    // Strip leading wake words repeatedly, tolerating punctuation:
    // "ultron! play music" -> "play music", "hey ultron hello" -> "hello".
    const wakeRe = /^(?:hey|ok|please|ultron|jarvis|zora)\b[^\w]*\s*/i;
    let prev;
    do {
      prev = cmd;
      cmd = cmd.replace(wakeRe, "").trim();
    } while (cmd !== prev);

    if (cmd) {
      setHeardText(cmd);
      const handler = onCommandRef.current;
      if (handler) handler(cmd);
    }
    capturingRef.current = false;
    finalTextRef.current = "";
    setWakeDetected(false);
    clearSilenceTimer();
  }, []);

  const armSilenceFlush = () => {
    clearSilenceTimer();
    silenceTimerRef.current = setTimeout(() => {
      // Flush whatever was accumulated, even if the browser never finalized it.
      if (capturingRef.current && finalTextRef.current.trim()) {
        dispatch(finalTextRef.current);
      }
    }, SILENCE_FLUSH_MS);
  };

  const start = useCallback(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    setVoiceError("");
    if (!SR) {
      const message = "Voice recognition is unavailable in this browser.";
      setVoiceError(message);
      console.warn(`[VOICE] ${message}`);
      return;
    }

    const generation = ++generationRef.current;
    const rec = new SR();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = RECOG_LANG;

    // True only while `rec` is the live recognizer for the current generation.
    const isCurrent = () =>
      recRef.current === rec && generationRef.current === generation;

    rec.onresult = (event) => {
      if (!isCurrent()) return;
      let interim = "";
      let final = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const res = event.results[i];
        if (res.isFinal) final += res[0].transcript;
        else interim += res[0].transcript;
      }
      const transcript = (final || interim || "").trim();
      const low = transcript.toLowerCase();
      if (!low) return;

      // 1. Command-capture mode: accumulate EVERY chunk (final + interim) and
      //    send ONCE on a pause — never drop the tail of a long command.
      if (capturingRef.current) {
        finalTextRef.current = (finalTextRef.current + " " + transcript).trim();
        setHeardText(finalTextRef.current);
        armSilenceFlush();
        return;
      }

      // 2. Wake-word detection — capture the WHOLE line in one shot.
      const { matched, rest } = matchesWakeWord(low);
      if (matched) {
        setWakeDetected(true);
        if (rest.length >= 2) {
          // Dispatch immediately (one-line command after the wake word).
          dispatch(rest);
          return;
        }
        // No command in this utterance yet → capture the next phrase.
        capturingRef.current = true;
        finalTextRef.current = "";
        armSilenceFlush();
      }
    };

    rec.onerror = (event) => {
      if (!isCurrent()) return;
      if (event.error === "not-allowed") {
        // Permission denied: stop retrying until the user re-enables voice.
        fatalRef.current = true;
        clearRestartTimer();
        const message = "Microphone permission was denied.";
        setVoiceError(message);
        console.warn(`[VOICE] ${message}`);
        try { rec.stop(); } catch (_e) {}
        return;
      }
      if (event.error === "service-not-allowed") {
        // Service blocked: stop retrying until the user re-enables voice.
        fatalRef.current = true;
        clearRestartTimer();
        const message = "Browser speech recognition service is unavailable.";
        setVoiceError(message);
        console.warn(`[VOICE] ${message}`);
        try { rec.stop(); } catch (_e) {}
        return;
      }
      if (event.error === "audio-capture") {
        // No microphone input right now (e.g. remote desktop/VM): show an
        // honest visible message, but keep auto-recovering in case a mic
        // becomes available (device plugged in / remote session grants one).
        backoffRef.current = Math.min(
          backoffRef.current * 2,
          MAX_RESTART_BACKOFF_MS
        );
        const message = "No microphone input is available in this browser or remote desktop — retrying…";
        setVoiceError(message);
        console.warn(`[VOICE] ${message}`);
        try { rec.stop(); } catch (_e) {}
        return;
      }
      if (event.error === "network") {
        // Transient connection hiccup with the speech service: soft notice,
        // grow the backoff, and let `onend` schedule an auto-restart.
        backoffRef.current = Math.min(
          backoffRef.current * 2,
          MAX_RESTART_BACKOFF_MS
        );
        const message = "Speech service connection hiccup — retrying…";
        setVoiceError(message);
        console.warn(`[VOICE] ${message}`);
        try { rec.stop(); } catch (_e) {}
        return;
      }
      // Other errors (no-speech, aborted, …): recover quietly.
      if (RECOVERABLE_ERRORS.has(event.error)) {
        backoffRef.current = Math.min(
          backoffRef.current * 2,
          MAX_RESTART_BACKOFF_MS
        );
      }
      try { rec.stop(); } catch (_e) {}
    };

    rec.onstart = () => {
      if (!isCurrent()) return;
      backoffRef.current = RESTART_BACKOFF_MS; // success resets the backoff
      setIsListening(true);
      setVoiceError("");
    };

    rec.onend = () => {
      if (!isCurrent()) return; // a stale recognizer must never restart itself
      setIsListening(false);
      // Final flush: if the browser ended mid-capture, send what we have.
      if (capturingRef.current && finalTextRef.current.trim()) {
        dispatch(finalTextRef.current);
      }
      if (enabledRef.current && !fatalRef.current) {
        // Deferred restart: lets the browser fully tear down this session
        // before starting again (avoids InvalidStateError from sync restarts).
        clearRestartTimer();
        restartTimerRef.current = setTimeout(() => {
          if (isCurrent() && enabledRef.current && !fatalRef.current) {
            try { rec.start(); } catch (_e) { /* next onend will retry */ }
          }
        }, backoffRef.current);
      }
    };

    recRef.current = rec;
    try {
      rec.start();
    } catch (_error) {
      fatalRef.current = true;
      setIsListening(false);
      setVoiceError("Voice recognition could not start in this browser.");
    }
  }, []);

  const stop = useCallback(() => {
    clearSilenceTimer();
    clearRestartTimer();
    const rec = recRef.current;
    recRef.current = null;
    generationRef.current++; // invalidate any pending callbacks/restarts
    if (rec) {
      // Detach handlers BEFORE aborting so the async `onend` can never
      // restart a stale recognizer or mutate state after stop().
      rec.onstart = rec.onresult = rec.onerror = rec.onend = null;
      try { rec.abort(); } catch (_e) {}
      try { rec.stop(); } catch (_e) {}
    }
    capturingRef.current = false;
    finalTextRef.current = "";
    setIsListening(false);
    setWakeDetected(false);
    setHeardText("");
  }, []);

  // Mic lifecycle in an effect: start when enabled, cleanly stop otherwise.
  useEffect(() => {
    if (enabled) {
      fatalRef.current = false;
      backoffRef.current = RESTART_BACKOFF_MS;
      start();
    } else {
      stop();
    }
    return () => { stop(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled]);

  // Cleanup on unmount (silence + pending restarts).
  useEffect(() => () => {
    clearSilenceTimer();
    clearRestartTimer();
  }, []);

  return { isListening, wakeDetected, heardText, voiceError, supported, start, stop };
}
