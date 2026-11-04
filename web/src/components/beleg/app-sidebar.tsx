import { Link, useRouterState } from "@tanstack/react-router";
import { CheckCheck, ClipboardCheck, LayoutDashboard, SlidersHorizontal, Upload, Receipt } from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { useBeleg } from "@/lib/beleg-store";
import { displayStatus } from "./status";

export function AppSidebar() {
  const path = useRouterState({ select: (s) => s.location.pathname });
  const { docs, mode } = useBeleg();
  const queue = docs.filter((d) => displayStatus(d) === "zu-pruefen").length;

  const items = [
    { title: "Übersicht", to: "/", icon: LayoutDashboard },
    { title: "Belege hochladen", to: "/hochladen", icon: Upload },
    { title: "Zu prüfen", to: "/pruefen", icon: ClipboardCheck, badge: queue },
    { title: "Freigegeben", to: "/freigegeben", icon: CheckCheck },
  ] as const;

  const isActive = (to: string) => (to === "/" ? path === "/" : path.startsWith(to));

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <div className="flex items-center gap-2.5 px-1 py-1.5">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
            <Receipt className="h-4 w-4" />
          </div>
          <div className="min-w-0 group-data-[collapsible=icon]:hidden">
            <p className="truncate text-sm font-semibold leading-tight">Beleg-Prüfung</p>
            <p className="truncate text-xs text-muted-foreground">Quellberg GmbH</p>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Buchhaltung</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.to}>
                  <SidebarMenuButton asChild isActive={isActive(item.to)} tooltip={item.title}>
                    <Link to={item.to}>
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                  {"badge" in item && item.badge > 0 && <SidebarMenuBadge>{item.badge}</SidebarMenuBadge>}
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>Konfiguration</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={isActive("/pruefregeln")} tooltip="Prüfregeln">
                  <Link to="/pruefregeln">
                    <SlidersHorizontal className="h-4 w-4" />
                    <span>Prüfregeln</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <div className="rounded-lg border bg-background/60 p-2.5 text-xs group-data-[collapsible=icon]:hidden">
          <div className="flex items-center gap-1.5 font-medium">
            <span className={`h-2 w-2 rounded-full ${mode === "live" ? "bg-success" : "bg-warning"}`} />
            {mode === "live" ? "Python-Backend verbunden" : "Demo-Daten"}
          </div>
          <p className="mt-1 text-muted-foreground">
            {mode === "live" ? "Analyse läuft über die bestehende Pipeline." : "Ergebnisse des letzten Laufs über 16 Testbelege."}
          </p>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
