import { useRef, useState, useCallback } from 'react';

/**
 * useVoice Hook — human-like wake-word voice.
 * Listens for a wake word and captures the FULL command in ONE line,
 * so "Hey Ultron what's the weather" sends the whole command (not just the name).
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

  const dispatch = (cmd) => {
    if (cmd) {
      setHeardText(cmd);
      if (onCommand) onCommand(cmd);
    }
    capturingRef.current = false;
    finalTextRef.current = "";
    setWakeDetected(false);
  };

  const start = useCallback(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      console.warn("[VOICE] Web Speech API not supported in this browser.");
      return;
    }

    const rec = new SR();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = "hi-IN";

    rec.onresult = (event) => {
      let interim = "";
      let final = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const res = event.results[i];
        if (res.isFinal) final += res[0].transcript;
        else interim += res[0].transcript;
      }
      const transcript = (final || interim || "").trim();
      const low = transcript.toLowerCase();

      // 1. Command-capture mode: accumulate + send on a pause.
      if (capturingRef.current) {
        finalTextRef.current = (finalTextRef.current + " " + transcript).trim();
        setHeardText(finalTextRef.current);
        // Send after a short silence (when this result is final).
        if (final) {
          const cmd = finalTextRef.current.replace(/^\s*(hey|ok|please)\s+/i, "").trim();
          dispatch(cmd);
        }
        return;
      }

      // 2. Wake-word detection — capture the WHOLE line in one shot.
      if (low) {
        const matched = WAKE_WORDS.find((w) => low.includes(w));
        if (matched) {
          setWakeDetected(true);
          // Everything AFTER the wake word is the command (same utterance).
          const idx = low.indexOf(matched);
          let rest = transcript.slice(idx + matched.length).trim();
          // If there's a command after the wake word, send it immediately (one-line).
          if (rest) {
            rest = rest.replace(/^[,.\s]+/, "").trim();
            if (rest.length >= 2) {
              // Dispatch the command, but keep listening for a follow-up.
              dispatch(rest);
              return;
            }
          }
          // No command in this utterance yet → capture the next phrase.
          capturingRef.current = true;
          finalTextRef.current = "";
        }
      }
    };

    rec.onerror = (event) => {
      if (event.error === "not-allowed") {
        console.warn("[VOICE] Microphone permission denied.");
      }
      try { rec.stop(); } catch (_e) {}
    };

    rec.onend = () => {
      if (enabled) { try { rec.start(); } catch (_e) {} }
    };

    recRef.current = rec;
    try { rec.start(); } catch (_e) {}
    setIsListening(true);
  }, [enabled, onCommand]);

  const stop = useCallback(() => {
    if (recRef.current) { try { recRef.current.stop(); } catch (_e) {} recRef.current = null; }
    capturingRef.current = false;
    finalTextRef.current = "";
    setIsListening(false);
    setWakeDetected(false);
    setHeardText("");
  }, []);

  if (enabled && !isListening && !recRef.current) {
    setTimeout(() => { if (enabled) start(); }, 0);
  } else if (!enabled && isListening) {
    stop();
  }

  return { isListening, wakeDetected, heardText, start, stop };
}
