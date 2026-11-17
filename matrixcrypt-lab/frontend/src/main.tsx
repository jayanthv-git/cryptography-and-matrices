import { StrictMode, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BookOpen,
  FlaskConical,
  Grid2X2,
  House,
  Menu,
  ScanLine,
  Waypoints,
  X,
} from "lucide-react";
import { Home } from "./Home";
import { CipherStudio, Playground } from "./CipherPages";
import { Recovery } from "./Recovery";
import { Experiments } from "./Experiments";
import { Research } from "./Research";
import "./style.css";
const pages = [
  { id: "", label: "Command Center", icon: House, component: Home },
  {
    id: "cipher",
    label: "Cipher Studio",
    icon: ScanLine,
    component: CipherStudio,
  },
  {
    id: "playground",
    label: "Matrix Playground",
    icon: Grid2X2,
    component: Playground,
  },
  {
    id: "recover",
    label: "Break the Cipher",
    icon: Waypoints,
    component: Recovery,
  },
  {
    id: "experiments",
    label: "Experiment Intelligence",
    icon: FlaskConical,
    component: Experiments,
  },
  {
    id: "research",
    label: "Research Observatory",
    icon: BookOpen,
    component: Research,
  },
];
function App() {
  const [route, setRoute] = useState(location.hash.slice(2));
  const [open, setOpen] = useState(false);
  const main = useRef<HTMLElement>(null);
  useEffect(() => {
    const change = () => {
      setRoute(location.hash.slice(2));
      setOpen(false);
      window.scrollTo(0, 0);
      main.current?.focus({ preventScroll: true });
    };
    window.addEventListener("hashchange", change);
    return () => window.removeEventListener("hashchange", change);
  }, []);
  const page = pages.find((p) => p.id === route);
  useEffect(() => {
    document.title = `${page?.label || "Page not found"} · MatrixCrypt Lab`;
  }, [page]);
  const Component = page?.component;
  return (
    <>
      <a
        className="skip-link"
        href="#main-content"
        onClick={(e) => {
          e.preventDefault();
          main.current?.focus({ preventScroll: true });
        }}
      >
        Skip to content
      </a>
      <aside className={`sidebar ${open ? "nav-open" : ""}`}>
        <a className="brand" href="#/" aria-label="MatrixCrypt Lab home">
          <span className="brand-mark">
            M<span>×</span>
          </span>
          <span>
            MatrixCrypt<small>LABORATORY</small>
          </span>
        </a>
        <button
          className="mobile-toggle"
          aria-expanded={open}
          aria-controls="main-navigation"
          aria-label={open ? "Close navigation" : "Open navigation"}
          onClick={() => setOpen(!open)}
        >
          {open ? <X /> : <Menu />}
        </button>
        <div className="sidebar-content" id="main-navigation">
          <span className="nav-caption">EXPLORE THE LAB</span>
          <nav aria-label="Main navigation">
            {pages.map((p, i) => (
              <a
                key={p.id}
                href={`#/${p.id}`}
                aria-current={route === p.id ? "page" : undefined}
              >
                <p.icon size={17} />
                <span>{p.label}</span>
                <small>{String(i).padStart(2, "0")}</small>
              </a>
            ))}
          </nav>
          <div className="sidebar-bottom">
            <span className="sidebar-formula">
              C = KP <small>mod 26</small>
            </span>
            <p>
              Linear algebra.
              <br />
              An open book.
            </p>
            <span className="sidebar-label">EDUCATIONAL USE ONLY</span>
          </div>
        </div>
      </aside>
      <div className="app-body">
        <header className="topbar">
          <span>A STUDY IN CRYPTOGRAPHY & MATRICES</span>
          <span className="topbar-right">
            <i /> 2 × 2 HILL CIPHER
          </span>
        </header>
        <main
          id="main-content"
          ref={main}
          tabIndex={-1}
          className={route === "" ? "home-main" : ""}
        >
          {Component ? (
            <Component key={route} />
          ) : (
            <div className="empty-state">
              <h1>Page not found</h1>
              <a href="#/">Return to Command Center</a>
            </div>
          )}
        </main>
        <footer>
          <span>
            MatrixCrypt Lab <span className="muted">/</span> Mathematics made
            visible.
          </span>
          <span>Classical cipher · Not for real secrets</span>
        </footer>
      </div>
    </>
  );
}
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
