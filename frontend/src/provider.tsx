import type { NavigateOptions } from "react-router-dom";

import { HeroUIProvider } from "@heroui/system";
import { useHref, useNavigate } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import { PayPalScriptProvider } from "@paypal/react-paypal-js";

declare module "@react-types/shared" {
  interface RouterConfig {
    routerOptions: NavigateOptions;
  }
}

// PayPal configuration
const paypalOptions = {
  clientId: import.meta.env.VITE_PAYPAL_CLIENT_ID || "test",
  currency: "USD",
  intent: "capture",
};

export function Provider({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();

  return (
    <HelmetProvider>
      <HeroUIProvider navigate={navigate} useHref={useHref}>
        <PayPalScriptProvider options={paypalOptions}>
          {children}
        </PayPalScriptProvider>
      </HeroUIProvider>
    </HelmetProvider>
  );
}
