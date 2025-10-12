import { Outlet } from "react-router-dom";

import { Chat } from "../chat/Chat";

import { Navbar } from "./Navbar";
import { Footer } from "./Footer";
import { SkipLink } from "./SkipLink";

export function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <SkipLink />
      <Navbar />
      <main
        className="flex-1 w-full"
        id="main-content"
        role="main"
        tabIndex={-1}
      >
        <Outlet />
      </main>
      <Footer />
      <Chat />
    </div>
  );
}
