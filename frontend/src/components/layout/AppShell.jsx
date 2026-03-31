import { useEffect, useRef, useState } from "react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { FiBell, FiBookOpen, FiMoon, FiSun } from "react-icons/fi";
import { useAuth } from "../../contexts/AuthContext";
import { useTheme } from "../../contexts/ThemeContext";
import { chatApi } from "../../api/client";
import SvgIcon from "./SvgIcon";
import styles from "./AppShell.module.scss";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: "home", roles: ["admin", "teacher", "student"] },
  { to: "/students", label: "Student Management", icon: "menu", roles: ["admin", "teacher"] },
  { to: "/upload", label: "CSV Upload", icon: "upload", roles: ["admin", "teacher"] },
  { to: "/analytics", label: "Insights", icon: "history", roles: ["admin", "teacher", "student"] },
  { to: "/scholarship", label: "Scholarship Detail", icon: "settings", roles: ["admin", "teacher", "student"] },
  { to: "/chat", label: "Chat Section", icon: "history", roles: ["admin", "teacher", "student"] },
];

export default function AppShell({ children, notifications = [] }) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);
  const [headerNotificationsOpen, setHeaderNotificationsOpen] = useState(false);
  const [chatNotifications, setChatNotifications] = useState([]);
  const accountCardRef = useRef(null);
  const headerNotificationsRef = useRef(null);

  const shellTone =
    theme === "dark"
      ? "min-h-screen bg-black text-white"
      : "min-h-screen bg-white text-black";

  const mutedText = theme === "dark" ? "text-white" : "text-slate-700";
  const navIdle = theme === "dark" ? "text-white hover:bg-white/10" : "text-black hover:bg-slate-100";
  const navActive = theme === "dark" ? "bg-white/15 text-white" : "bg-slate-100 text-black";
  const profileCard = theme === "dark" ? "border-white/20 bg-slate-900 text-white" : "border-slate-200 bg-white text-black";
  const roleText = theme === "dark" ? "text-white" : "text-black";
  const sidebarTone =
    theme === "dark"
      ? "bg-slate-900"
      : "bg-white";
  const brandCardTone = theme === "dark" ? "border-white/10 bg-slate-900" : "border-slate-200 bg-white";
  const brandIconTone = theme === "dark" ? "border-white/20 bg-slate-900 text-white" : "border-slate-300 bg-white text-black";
  const brandTitleTone =
    theme === "dark"
      ? "text-[#E98074]"
      : "text-[#E85A4F]";
  const role = String(user?.role || "").toLowerCase();
  const visibleNavItems = [
    ...navItems.filter((item) => !item.roles || item.roles.includes(role)),
    { to: "/profile", label: "Edit Profile", icon: "settings" },
  ];
  const notificationMenuTone =
    theme === "dark"
      ? "border-white/20 bg-slate-900 text-white"
      : "border-slate-200 bg-white text-black";
  const notificationMenuSubtextTone = theme === "dark" ? "text-slate-200" : "text-slate-700";
  const notificationItemTone =
    theme === "dark"
      ? "border-white/15 bg-slate-900 text-white"
      : "border-slate-200/80 bg-white text-black";
  const notificationMessageTone = theme === "dark" ? "text-slate-100" : "text-slate-800";
  const mergedNotifications = [...(notifications || []), ...(chatNotifications || [])].filter((item, index, array) => {
    const key = item.id || `${item.title}-${item.message}`;
    return index === array.findIndex((entry) => (entry.id || `${entry.title}-${entry.message}`) === key);
  });

  const openAuthMode = (mode) => {
    logout();
    setAccountMenuOpen(false);
    navigate(`/login?mode=${mode}`);
  };

  const switchAccount = () => {
    logout();
    setAccountMenuOpen(false);
    navigate("/login");
  };

  useEffect(() => {
    const onClickOutside = (event) => {
      if (!accountCardRef.current?.contains(event.target)) {
        setAccountMenuOpen(false);
      }
      if (!headerNotificationsRef.current?.contains(event.target)) {
        setHeaderNotificationsOpen(false);
      }
    };

    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  useEffect(() => {
    const role = String(user?.role || "").toLowerCase();
    if (role !== "student") {
      setChatNotifications([]);
      return;
    }

    const loadImportantChatNotifications = async () => {
      try {
        const res = await chatApi.listMessages();
        setChatNotifications(Array.isArray(res?.data?.important_notifications) ? res.data.important_notifications : []);
      } catch {
        setChatNotifications([]);
      }
    };

    loadImportantChatNotifications();
  }, [location.pathname, user?.role]);

  return (
    <div className={`${styles.shell} ${theme === "dark" ? styles.shellDark : ""} ${shellTone}`}>
      <div className="grid w-full gap-6 p-4 md:p-6 xl:grid-cols-[20%_80%] xl:items-start">
        <aside className={`glass sticky top-4 hidden h-[calc(100vh-32px)] w-full flex-col p-5 xl:flex ${sidebarTone}`}>
          <div className={`mb-8 rounded-2xl border p-4 ${brandCardTone}`}>
            <div className={`mb-3 inline-flex rounded-xl border p-2 ${brandIconTone}`}>
              <FiBookOpen className="h-5 w-5" />
            </div>
            <h1 className={`text-4xl font-bold leading-tight ${brandTitleTone}`}>Student Retento</h1>
          </div>

          <nav className="space-y-2">
            {visibleNavItems.map((item) => {
              const active = location.pathname === item.to || (item.to === "/analytics" && location.pathname.startsWith("/students/"));
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-xl font-semibold transition ${
                    active ? navActive : navIdle
                  }`}
                >
                  <SvgIcon name={item.icon} className="h-6 w-6" />
                  {item.label}
                </NavLink>
              );
            })}
          </nav>

          <div ref={accountCardRef} className={`mt-auto rounded-xl border p-3 text-sm ${profileCard}`}>
            <p className="font-semibold text-slate-900 dark:text-slate-100">Signed in as</p>
            <p>{user?.name}</p>
            <p className={`uppercase tracking-wide ${roleText}`}>{user?.role}</p>
            <button
              className="mt-3 ghost-btn w-full justify-center"
              onClick={() => setAccountMenuOpen((prev) => !prev)}
              type="button"
            >
              Account Options
            </button>
            {accountMenuOpen && (
              <div className="mt-2 space-y-2 rounded-lg border border-slate-200/80 bg-white/95 p-2 dark:border-white/20 dark:bg-slate-900/90">
                <Link className="ghost-btn w-full justify-center" to="/profile" onClick={() => setAccountMenuOpen(false)}>
                  Check Profile
                </Link>
                <button className="ghost-btn w-full justify-center" onClick={() => openAuthMode("login")} type="button">
                  Login
                </button>
                <button className="ghost-btn w-full justify-center" onClick={() => openAuthMode("signup")} type="button">
                  Sign up
                </button>
                <button className="ghost-btn w-full justify-center" onClick={switchAccount} type="button">
                  Switch Account
                </button>
              </div>
            )}
          </div>
        </aside>

        <main className="min-w-0 space-y-4 xl:col-start-2">
          <header className="glass relative z-40 flex flex-wrap items-center justify-between gap-3 overflow-visible px-4 py-3">
            <div>
              <h2 className="page-title">{location.pathname === "/dashboard" ? "Dashboard" : "Student Retento"}</h2>
              <p className={`page-description ${mutedText}`}>AI-powered insights for intervention planning</p>
            </div>
            <div className="relative flex items-center gap-2" ref={headerNotificationsRef}>
              <button
                className="ghost-btn"
                onClick={() => setHeaderNotificationsOpen((prev) => !prev)}
                type="button"
                aria-expanded={headerNotificationsOpen}
                aria-haspopup="menu"
                title="Open notifications"
              >
                <FiBell />
                Notifications
                <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-semibold text-blue-700 dark:bg-blue-500/20 dark:text-blue-200">
                  {(mergedNotifications || []).length}
                </span>
              </button>
              {headerNotificationsOpen && (
                <div className={`absolute right-0 top-full z-[120] mt-2 w-[30rem] rounded-xl border p-4 shadow-2xl ${notificationMenuTone}`} role="menu" aria-label="Notifications menu">
                  <p className="text-xl font-bold">Notifications</p>
                  <p className={`mt-1 text-base font-semibold ${notificationMenuSubtextTone}`}>AI-powered insights for intervention planning</p>
                  <div className="mt-3 max-h-80 space-y-3 overflow-auto pr-1">
                    {(mergedNotifications || []).length === 0 ? (
                      <p className={`text-base ${notificationMenuSubtextTone}`}>No student updates right now.</p>
                    ) : (
                      (mergedNotifications || []).slice(0, 10).map((note) => {
                        const severity = String(note.severity || "info").toLowerCase();
                        const badgeTone =
                          severity === "high"
                            ? "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-200"
                            : severity === "medium"
                              ? "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-200"
                              : "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-200";

                        return (
                          <div key={note.id || `${note.title}-${note.message}`} className={`rounded-lg border p-3 ${notificationItemTone}`}>
                            <div className="flex items-center justify-between gap-2">
                              <p className="text-lg font-bold leading-snug">{note.title || "Update"}</p>
                              <span className={`rounded-full px-3 py-1 text-sm font-bold uppercase ${badgeTone}`}>
                                {severity}
                              </span>
                            </div>
                            <p className={`mt-2 text-base font-semibold ${notificationMessageTone}`}>{note.message || "Student update available."}</p>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>
              )}

              <button className="ghost-btn" onClick={toggleTheme}>
                {theme === "dark" ? <FiSun /> : <FiMoon />}
                {theme === "dark" ? "Light" : "Dark"}
              </button>
              <button className="ghost-btn" onClick={logout}>
                <SvgIcon name="close" className="h-5 w-5" /> Logout
              </button>
              <Link to="/dashboard" className="ghost-btn lg:hidden">
                <SvgIcon name="home" className="h-5 w-5" /> Home
              </Link>
            </div>
          </header>

          <section>{children}</section>
        </main>
      </div>
    </div>
  );
}
