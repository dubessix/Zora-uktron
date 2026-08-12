import { useRef, useState, useCallback } from 'react';

/**
 * useVoice Hook
 * Lightweight, browser-native voice control using the Web Speech API
 * (webkitSpeechRecognition). No backend STT, no heavy local model — ideal for
 * low-spec machines (8GB RAM / dual-core).
 *
 * Flow:
 *  - When enabled, it listens continuously for a WAKE WORD.
 *  - On wake word, it switches to "command" mode and captures the next phrase.
 *  - The captured command is returned via onCommand().
 */
const WAKE_WORDS = [
  "ultron", "jarvis", "zora", "hey ultron", "hi ultron",
  "ok ultron", "wake up", "iron man", "activate"
];

export default function useVoice({ onCommand, enabled }) {
  const [isListening, setIsListening] = useState(false);
  const [wakeDetected, setWakeDetected] = useState(false);
  const [heardText, setHeardText] = useState("");
  const recRef = useRef(null);
  const capturingRef = useRef(false);
  const finalTextRef = useRef("");

  const restart = useCallback((rec) => {
    try {
      rec.stop();
      rec.start();
    } catch (_e) {
      /* ignore restart races */
    }
  }, []);

  const start = useCallback(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      console.warn("[VOICE] Web Speech API not supported in this browser.");
      return;
    }

    const rec = new SR();
    rec.continuous = true;
    rec.interimResults = true;
    // Multilingual capture: Hinglish + English + Hindi mixed speech.
    // Web Speech only supports one lang at a time; hi-IN transcribes both
    // Hindi and English (Hinglish) so Ultron understands mixed talk.
    rec.lang = "hi-IN";

    rec.onresult = (event) => {
      let interim = "";
      let final = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const res = event.results[i];
        if (res.isFinal) final += res[0].transcript;
        else interim += res[0].transcript;
      }
      const full = (final || interim || "").trim().toLowerCase();

      if (capturingRef.current) {
        // In command-capture mode: accumulate final text.
        if (final) {
          finalTextRef.current = (finalTextRef.current + " " + final).trim();
          setHeardText(finalTextRef.current);
          // A short silence usually means the phrase ended — dispatch.
          const cmd = finalTextRef.current;
          finalTextRef.current = "";
          capturingRef.current = false;
          setWakeDetected(false);
          if (onCommand && cmd) onCommand(cmd);
        }
        return;
      }

      // Wake-word detection mode.
      if (full) {
        const matched = WAKE_WORDS.find((w) => full.includes(w));
        if (matched) {
          setWakeDetected(true);
          capturingRef.current = true;
          finalTextRef.current = "";
        }
      }
    };

    rec.onerror = (event) => {
      if (event.error === "not-allowed") {
        console.warn("[VOICE] Microphone permission denied.");
      }
      // Non-fatal: let the continuous loop restart.
      try { rec.stop(); } catch (_e) {}
    };

    rec.onend = () => {
      // Keep listening while the mic toggle is still on.
      if (enabled) {
        try { rec.start(); } catch (_e) {}
      }
    };

    recRef.current = rec;
    try { rec.start(); } catch (_e) {}
    setIsListening(true);
  }, [enabled, onCommand]);

  const stop = useCallback(() => {
    if (recRef.current) {
      try { recRef.current.stop(); } catch (_e) {}
      recRef.current = null;
    }
    capturingRef.current = false;
    finalTextRef.current = "";
    setIsListening(false);
    setWakeDetected(false);
    setHeardText("");
  }, []);

  // React to `enabled` changes.
  if (enabled && !isListening && !recRef.current) {
    // start after render tick to avoid StrictMode double-start
    setTimeout(() => { if (enabled) start(); }, 0);
  } else if (!enabled && isListening) {
    stop();
  }

  return { isListening, wakeDetected, heardText, start, stop };
}
