import { NavLink } from "react-router-dom";
import "./BottomNav.css";

interface NavItem {
  to: string;
  icon: string;
  label: string;
}

const navItems: NavItem[] = [
  { to: "/journal", icon: "\uD83D\uDCD6", label: "Journal" },
  { to: "/calendar", icon: "\uD83D\uDCC5", label: "Calendar" },
  { to: "/profile", icon: "\uD83D\uDC64", label: "Profile" },
];

export default function BottomNav() {
  return (
    <nav className="bottom-nav">
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `bottom-nav__link${isActive ? " active" : ""}`
          }
        >
          <span className="bottom-nav__icon">{item.icon}</span>
          <span>{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
