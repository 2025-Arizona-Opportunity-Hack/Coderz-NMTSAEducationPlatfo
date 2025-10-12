import React, { useEffect, useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { motion } from "framer-motion";
import { X, Key, AlertTriangle, Cpu, Zap } from "lucide-react";
import { isWebGPUSupported } from "@/lib/webllm";
import { toggleLocal, getProvider, isLocalEnabled } from "@/lib/ai";

interface GenaiDialogProps {
  isOpen: boolean;
  onSubmitApiKey: (apiKey: string) => void;
  onUseLocal: (statusMessage: string) => void; // receives status text after toggle
  onClose: () => void;
}

export const GenaiDialog: React.FC<GenaiDialogProps> = ({
  isOpen,
  onSubmitApiKey,
  onUseLocal,
  onClose,
}) => {
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState("");
  const [localStatus, setLocalStatus] = useState<
    "idle" | "checking" | "ready" | "unsupported" | "error"
  >("idle");
  const { toast } = useToast();
  const [progress, setProgress] = useState<number | null>(null);
  const [localMessage, setLocalMessage] = useState("");

  useEffect(() => {
    if (!isOpen) return;
    const enabled = isLocalEnabled() && getProvider() === "local";
    if (!isWebGPUSupported()) {
      setLocalStatus("unsupported");
      setLocalMessage(
        "WebGPU is not available. Please enable hardware acceleration in your browser settings and use a compatible browser (Chrome, Edge, or Firefox Nightly).",
      );
      return;
    }
    if (enabled) {
      setLocalStatus("ready");
      setLocalMessage("Local AI is ready. Click to disable.");
    } else {
      setLocalStatus("idle");
      setLocalMessage("Your browser supports WebGPU.");
    }
  }, [isOpen]);

  const handleEnableLocal = async () => {
    if (!isWebGPUSupported()) {
      setLocalStatus("unsupported");
      toast({
        title: "WebGPU Not Supported",
        description:
          "WebGPU is not supported in your browser. Please enable hardware acceleration or use a compatible browser (Chrome, Edge, or Firefox Nightly).",
        variant: "destructive",
      });
      return;
    }
    try {
      if (localStatus === "ready") {
        // Disable
        const resp = await toggleLocal();
        setLocalStatus("idle");
        setLocalMessage("Local AI disabled.");
        onUseLocal(resp.content || "Local AI disabled.");
        return;
      }
      setLocalStatus("checking");
      setLocalMessage(
        "Loading local AI model (may take many minutes first time)...",
      );
      setProgress(null);
      const resp = await toggleLocal();
      if (resp.success && getProvider() === "local") {
        setLocalStatus("ready");
        setLocalMessage("Local AI is ready. Click again to disable.");
        onUseLocal(resp.content);
        onClose();
      } else if (!resp.success) {
        setLocalStatus("error");
        setLocalMessage(resp.content);
      } else {
        // Fallback case
        setLocalStatus("idle");
        setLocalMessage("Local AI disabled.");
        onUseLocal(resp.content);
      }
    } catch {
      setLocalStatus("error");
      setLocalMessage("An error occurred while preparing local AI.");
      setProgress(null);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey.trim()) {
      setError("Please enter a valid API key");
      return;
    }
    if (!apiKey.startsWith("AIza")) {
      setError("Gemini API keys typically start with 'AIza'");
      return;
    }
    onSubmitApiKey(apiKey.trim());
    setApiKey("");
    setError("");
  };

  const handleClose = () => {
    setApiKey("");
    setError("");
    setLocalStatus("idle");
    setLocalMessage("");
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-background border rounded-lg shadow-xl max-w-md w-full p-6 h-3/4 overflow-auto scrollbar-thin scrollbar-thumb-palette-gray-light/40 scrollbar-track-transparent pr-8"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold">Enable AI</h3>
          </div>
          <button
            onClick={handleClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mb-4 p-3 bg-accent/20 border border-border rounded-lg">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-palette-teal-DEFAULT dark:text-palette-teal-dark mt-0.5 flex-shrink-0" />
            <div className="text-sm text-muted-foreground">
              <p className="font-medium mb-1 text-foreground">
                Privacy Notice:
              </p>
              <p>
                <strong>Local AI (WebLLM):</strong> All processing happens in
                your browser using WebGPU. No keys or data ever leave your
                device.
                <br />
                <strong>Gemini (API key):</strong> Your API key is stored only
                in memory and will be lost when you refresh the page. All AI
                processing happens in your browser—your data stays with you.
              </p>
            </div>
          </div>
        </div>

        {/* Local LLM Section */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-palette-teal-DEFAULT dark:text-palette-teal-dark" />
            <h4 className="font-medium">Use Local AI (WebLLM)</h4>
          </div>
          <p className="text-sm text-muted-foreground">
            {localMessage ||
              "Run a small model in-browser with hardware acceleration."}
          </p>
          {localStatus === "checking" && (
            <div className="w-full bg-border rounded h-2 mb-2 overflow-hidden">
              <div
                className="bg-palette-teal h-2 rounded"
                style={{
                  width:
                    progress !== null
                      ? `${Math.round(progress * 100)}%`
                      : "30%",
                }}
              />
            </div>
          )}
          <button
            onClick={handleEnableLocal}
            disabled={
              localStatus === "checking" || localStatus === "unsupported"
            }
            className="w-full px-4 py-2 border border-border rounded-md hover:bg-muted transition-colors disabled:opacity-60"
          >
            {localStatus === "checking"
              ? "Preparing..."
              : localStatus === "ready"
                ? "Disable local AI"
                : localStatus === "unsupported"
                  ? "WebGPU not available"
                  : "Enable local AI"}
          </button>
        </div>

        {/* Divider */}
        <div className="my-6 flex items-center gap-3 text-xs text-muted-foreground">
          <div className="h-px bg-border flex-1" />
          <span>OR</span>
          <div className="h-px bg-border flex-1" />
        </div>

        {/* Gemini API Key Section */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-primary" />
            <h4 className="font-medium">Use Gemini (API key)</h4>
          </div>
          <div>
            <label htmlFor="apiKey" className="block text-sm font-medium mb-2">
              Gemini API Key
            </label>
            <input
              id="apiKey"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="AIza..."
              className="w-full px-3 py-2 border border-border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            />
            {error && (
              <p className="text-sm text-red-500 dark:text-red-400 mt-1">
                {error}
              </p>
            )}
          </div>

          <div className="text-xs text-muted-foreground">
            <p>
              Get your free API key from{" "}
              <a
                href="https://aistudio.google.com/apikey"
                target="_blank"
                rel="noopener noreferrer"
                className="text-palette-teal-DEFAULT dark:text-palette-teal-dark hover:underline"
              >
                Google AI Studio
              </a>
            </p>
          </div>

          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-4 py-2 border border-border rounded-md hover:bg-muted transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              Continue
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

export default GenaiDialog;
