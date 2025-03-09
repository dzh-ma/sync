import { createBrowserRouter } from "react-router-dom";
import Dashboard from "./dashboard/page";
import Login from "./auth/login/page";
import Register from "./auth/signup/page";
import AddDevice from "./add-device/page";
import AddRoom from "./add-room/page";
import Automations from "./automations/page";
import CreateProfile from "./create-profile/page";
import Devices from "./devices/page";
import ManageProfiles from "./manage-profiles/page";
import Profile from "./profile/page";
import Rooms from "./rooms/page";
import Settings from "./settings/page";
import Statistics from "./statistics/page";
import Suggestions from "./suggestions/page";
import HomePage from "./page";

const router = createBrowserRouter([
  {
    path: "/",
    element: <HomePage />,
  },
  {
    path: "/dashboard",
    element: <Dashboard />,
  },
  {
    path: "/auth/login",
    element: <Login />,
  },
  {
    path: "/auth/register",
    element: <Register />,
  },
  {
    path: "/add-device",
    element: <AddDevice />,
  },
  {
    path: "/add-room",
    element: <AddRoom />,
  },
  {
    path: "/automations",
    element: <Automations />,
  },
  {
    path: "/create-profile",
    element: <CreateProfile />,
  },
  {
    path: "/devices",
    element: <Devices />,
  },
  {
    path: "/manage-profiles",
    element: <ManageProfiles />,
  },
  {
    path: "/profile",
    element: <Profile />,
  },
  {
    path: "/rooms",
    element: <Rooms />,
  },
  {
    path: "/settings",
    element: <Settings />,
  },
  {
    path: "/statistics",
    element: <Statistics />,
  },
  {
    path: "/suggestions",
    element: <Suggestions />,
  },
]);

export default router;
