import type { ReactNode } from "react";

import { Home, Layers3, Radar, Search, Sparkles, Workflow } from "lucide-react";
import { Link, NavLink } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/", label: "Dashboard", icon: Home },
  { to: "/topics", label: "Topics", icon: Layers3 },
  { to: "/workspace", label: "Nouveau travail", icon: Sparkles },
  { to: "/reads", label: "Reads", icon: Radar },
  { to: "/lookup", label: "Lookup", icon: Search },
];

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(15,118,110,0.16),transparent_24%),linear-gradient(180deg,#f8f5ee_0%,#f4efe7_100%)]">
      <div className="mx-auto grid min-h-screen max-w-[1600px] grid-cols-[280px_minmax(0,1fr)] gap-5 px-5 py-5 max-[1100px]:grid-cols-1">
        <aside className="sticky top-5 self-start max-[1100px]:static">
          <Card className="mb-4 overflow-hidden bg-white/80 backdrop-blur">
            <CardContent className="space-y-5">
              <div className="space-y-3">
                <Badge className="bg-primary text-primary-foreground">Shadow PO AI</Badge>
                <div>
                  <h1 className="font-display text-2xl">Workspace Produit</h1>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Topic - Timeline - Artefact courant - Actions suivantes.
                  </p>
                </div>
              </div>

              <nav className="grid gap-2">
                {navItems.map(({ to, label, icon: Icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    className={({ isActive }) =>
                      cn(
                        "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition",
                        isActive ? "bg-accent text-accent-foreground" : "hover:bg-secondary"
                      )
                    }
                  >
                    <Icon className="h-4 w-4" />
                    <span>{label}</span>
                  </NavLink>
                ))}
              </nav>
            </CardContent>
          </Card>

          <Card className="bg-white/70">
            <CardContent className="space-y-4">
              <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <Workflow className="h-4 w-4" />
                Reprendre
              </div>
              <div>
                <h2 className="text-lg font-semibold">Continuité de travail</h2>
                <p className="mt-2 text-sm text-muted-foreground">
                  Revenir sur un topic, relire un run ou reprendre une continuation depuis le bon point d’entrée.
                </p>
              </div>
              <div className="grid gap-2">
                <Link className="rounded-2xl bg-secondary px-4 py-3 text-sm" to="/topics">
                  Ouvrir les topics
                </Link>
                <Link className="rounded-2xl bg-secondary px-4 py-3 text-sm" to="/lookup">
                  Relire un artefact
                </Link>
              </div>
            </CardContent>
          </Card>
        </aside>

        <div className="min-w-0">
          <header className="sticky top-5 z-20 mb-5 flex items-center justify-between gap-4 rounded-[28px] border border-border bg-white/75 px-6 py-4 shadow-soft backdrop-blur max-[900px]:static max-[900px]:flex-col max-[900px]:items-start">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Vue d'ensemble</p>
              <h2 className="font-display text-3xl">Shadow PO AI Workspace</h2>
            </div>
            <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
              <span className="rounded-full bg-secondary px-3 py-2">FastAPI backend live</span>
              <span className="rounded-full bg-secondary px-3 py-2">Read-first workflows</span>
              <span className="rounded-full bg-secondary px-3 py-2">Topics & timeline</span>
            </div>
          </header>

          {children}
        </div>
      </div>
    </div>
  );
}
