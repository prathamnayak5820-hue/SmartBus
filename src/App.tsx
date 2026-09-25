import { useEffect, useState } from "react";
import {
  Bus,
  MapPin,
  Users,
  Clock3,
  Network,
  ShieldAlert,
  Activity,
  Search,
  Wifi,
  Navigation,
  CheckCircle2,
  AlertTriangle,
  LayoutDashboard,
  CalendarClock,
  GraduationCap,
} from "lucide-react";

import Login from "./Login";
import api from "./api";

const menus = [
  ["Overview", LayoutDashboard],
  ["Live Tracking", MapPin],
  ["Attendance", Users],
  ["Buses & Routes", Bus],
  ["ETA Intelligence", Clock3],
  ["Network Health", Network],
  ["Alerts & SOS", ShieldAlert],
  ["Trip History", CalendarClock],
  ["Reports", Activity],
] as const;

const buses = [
  {
    id: "SB-101",
    route: "Udupi → SMVITM Bantakal",
    driver: "Ravi Kumar",
    students: 32,
    capacity: 40,
    speed: 34,
    eta: 12,
    status: "ON ROUTE",
  },
  {
    id: "SB-102",
    route: "Manipal → SMVITM",
    driver: "Arun Shetty",
    students: 28,
    capacity: 35,
    speed: 29,
    eta: 18,
    status: "ON ROUTE",
  },
  {
    id: "SB-103",
    route: "Kaup → SMVITM",
    driver: "Kiran Rao",
    students: 26,
    capacity: 40,
    speed: 0,
    eta: 24,
    status: "DELAYED",
  },
  {
    id: "SB-104",
    route: "Kundapura → SMVITM",
    driver: "Manoj P.",
    students: 30,
    capacity: 40,
    speed: 31,
    eta: 32,
    status: "ON ROUTE",
  },
];

export default function App() {
  const [token, setToken] = useState(
    () => localStorage.getItem("smartbus_token") || ""
  );

  const [user, setUser] = useState<any>(null);

  const [page, S] = useState("Overview");
  const [apiStatus, A] = useState("Checking");
  const [notice, N] = useState("");
  const [search, Q] = useState("");
  const [fallback, F] = useState(false);
  const [sos, E] = useState(false);
  const [present, P] = useState(32);
  const [moving, M] = useState(false);

  useEffect(() => {
    api
      .get("/")
      .then(() => A("Backend connected"))
      .catch(() => A("Backend offline"));
  }, []);

  const act = (message: string) => {
    N(message);
    setTimeout(() => N(""), 3000);
  };

  const handleLogin = (newToken: string, loggedInUser: any) => {
    localStorage.setItem("smartbus_token", newToken);
    setToken(newToken);
    setUser(loggedInUser);
    A("Backend connected");
  };

  const handleLogout = () => {
    localStorage.removeItem("smartbus_token");
    setToken("");
    setUser(null);
    S("Overview");
    A("Checking");
  };

  if (!token) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app">
      <aside>
        <div className="brand">
          <div className="logo">
            <Bus />
          </div>
          <div>
            <b>
              Smart<span>Bus</span>
            </b>
            <small>TRANSPORT INTELLIGENCE</small>
          </div>
        </div>

        <div className="college">
          <GraduationCap /> SMVITM Bantakal
        </div>

        <small className="label">WORKSPACE</small>

        {menus.map(([name, Icon]) => (
          <button
            className={"nav " + (page === name ? "active" : "")}
            onClick={() => S(name)}
            key={name}
          >
            <Icon size={18} />
            {name}
          </button>
        ))}

        <div className="sidebottom">
          {user?.name || "Transport Admin"}
          <br />
          <small>{user?.role || "Administrator"}</small>
          <br />
          <button className="secondary" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </aside>

      <main>
        <header>
          <span>
            SmartBus　/　<b>{page}</b>
          </span>
          <span className="status">● {apiStatus}</span>
        </header>

        <section className="content">
          <div className="heading">
            <div>
              <small className="eyebrow">SMARTBUS CONTROL CENTER</small>
              <h1>{page}</h1>
              <p>
                Intelligent college bus tracking, attendance and transport
                monitoring.
              </p>
            </div>

            <button
              className="primary"
              onClick={() => {
                M(!moving);
                act(
                  moving
                    ? "Simulation paused"
                    : "Demo bus movement started"
                );
              }}
            >
              <Activity size={16} />
              {moving ? "Pause demo" : "Simulate live trip"}
            </button>
          </div>

          {page === "Overview" && (
            <>
              <div className="metrics">
                <Metric
                  icon={Bus}
                  title="Active buses"
                  value="8"
                  sub="6 currently on route"
                />
                <Metric
                  icon={Users}
                  title="Students present"
                  value="186"
                  sub="Across active trips"
                />
                <Metric
                  icon={Navigation}
                  title="Active trips"
                  value="6"
                  sub="2 scheduled next"
                />
                <Metric
                  icon={Wifi}
                  title="Network health"
                  value="94%"
                  sub="Illustrative demo"
                />
              </div>

              <div className="columns">
                <section className="panel map">
                  <div className="panelhead">
                    <div>
                      <h3>Live fleet overview</h3>
                      <p>Illustrative route map · demo coordinates</p>
                    </div>
                    <span className="pill green">
                      {moving ? "● SIMULATION LIVE" : "● DEMO DATA"}
                    </span>
                  </div>

                  <div className="maparea">
                    <div className="road r1"></div>
                    <div className="road r2"></div>
                    <div className="routepath"></div>

                    {["UDUPI", "KAUP", "KATAPADY", "BANTAKAL", "SMVITM"].map(
                      (s, i) => (
                        <span className={"place p" + i} key={s}>
                          {s}
                        </span>
                      )
                    )}

                    {buses.map((b, i) => (
                      <button
                        className={"marker m" + i}
                        key={b.id}
                        onClick={() => act(b.id + " selected · " + b.route)}
                      >
                        <Bus size={15} />
                        {b.id}
                      </button>
                    ))}
                  </div>

                  <div className="legend">
                    🔵 Active bus　 ━ Planned route　{" "}
                    <span>Map schematic · not to scale</span>
                  </div>
                </section>

                <section className="panel">
                  <div className="panelhead">
                    <div>
                      <h3>Selected bus · SB-101</h3>
                      <p>Trip snapshot</p>
                    </div>
                    <span className="pill green">ON ROUTE</span>
                  </div>

                  <h2>Udupi → SMVITM</h2>

                  <div className="stats">
                    <div>
                      <small>ETA</small>
                      <b>12 min</b>
                    </div>
                    <div>
                      <small>Speed</small>
                      <b>34 km/h</b>
                    </div>
                    <div>
                      <small>Students</small>
                      <b>{present}/40</b>
                    </div>
                  </div>

                  <Info label="Driver" value="Ravi Kumar" />
                  <Info
                    label="Network"
                    value={
                      fallback
                        ? "Driver weak · student source selected"
                        : "Good"
                    }
                  />
                  <Info
                    label="Location source"
                    value={
                      fallback ? "Eligible student phone" : "Driver phone"
                    }
                  />
                  <Info
                    label="GPS freshness"
                    value={
                      moving ? "Updating (simulation)" : "Demo snapshot"
                    }
                  />

                  <button
                    className="secondary full"
                    onClick={() => S("Live Tracking")}
                  >
                    View live tracking →
                  </button>
                </section>
              </div>

              <div className="columns lower">
                <section className="panel">
                  <div className="panelhead">
                    <h3>Active trips</h3>
                    <button className="link" onClick={() => S("Buses & Routes")}>
                      View all →
                    </button>
                  </div>

                  <table>
                    <thead>
                      <tr>
                        <th>BUS</th>
                        <th>ROUTE</th>
                        <th>STUDENTS</th>
                        <th>ETA</th>
                        <th>STATUS</th>
                      </tr>
                    </thead>
                    <tbody>
                      {buses.map((b) => (
                        <tr key={b.id}>
                          <td>
                            <b>{b.id}</b>
                          </td>
                          <td>{b.route}</td>
                          <td>
                            {b.students}/{b.capacity}
                          </td>
                          <td>{b.eta} min</td>
                          <td>
                            <span className="pill green">{b.status}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </section>

                <section className="panel">
                  <h3>Recent alerts</h3>
                  <Info
                    label="Bus approaching Kaup"
                    value="SB-101 · 1 km remaining"
                  />
                  <Info
                    label="Network degraded"
                    value="SB-103 · Weak driver signal"
                  />
                  <Info
                    label="Student presence"
                    value="SB-101 · Attendance updated"
                  />
                  {sos && (
                    <Info label="SOS · DEMO" value="SB-103 simulated alert" />
                  )}
                </section>
              </div>
            </>
          )}

          {page === "Attendance" && (
            <>
              <div className="metrics">
                <Metric
                  icon={Users}
                  title="Registered"
                  value="40"
                  sub="Assigned to SB-101"
                />
                <Metric
                  icon={CheckCircle2}
                  title="Present"
                  value={String(present)}
                  sub="Phone detected · demo"
                />
                <Metric
                  icon={AlertTriangle}
                  title="Not detected"
                  value={String(40 - present)}
                  sub="No presence event"
                />
              </div>

              <section className="panel">
                <div className="panelhead">
                  <div>
                    <h3>Trip attendance · SB-101</h3>
                    <p>BLE presence sample records</p>
                  </div>

                  <button
                    className="primary"
                    onClick={() => {
                      P(Math.min(40, present + 1));
                      act("Demo presence added");
                    }}
                  >
                    + Simulate boarding
                  </button>
                </div>

                <div className="search">
                  <Search size={16} />
                  <input
                    value={search}
                    onChange={(e) => Q(e.target.value)}
                    placeholder="Search students..."
                  />
                </div>

                <table>
                  <thead>
                    <tr>
                      <th>STUDENT</th>
                      <th>ID</th>
                      <th>BOARDING POINT</th>
                      <th>FIRST SEEN</th>
                      <th>LAST SEEN</th>
                      <th>STATUS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      ["Rahul Kumar", "4MW25CS101", "Kaup", "7:42 AM", "8:04 AM", "PRESENT"],
                      ["Ananya Shetty", "4MW25CS102", "Katapady", "7:51 AM", "8:05 AM", "PRESENT"],
                      ["Aditya Rao", "4MW25CS103", "Udupi", "7:36 AM", "8:01 AM", "PRESENT"],
                      ["Nisha Pai", "4MW25CS104", "Bantakal", "—", "—", "NOT DETECTED"],
                      ["Kiran Acharya", "4MW25CS105", "Kaup", "7:43 AM", "7:58 AM", "LEFT"],
                    ]
                      .filter((r) =>
                        r.join(" ").toLowerCase().includes(search.toLowerCase())
                      )
                      .map((r) => (
                        <tr key={r[1]}>
                          {r.map((v, i) => (
                            <td key={i}>{v}</td>
                          ))}
                        </tr>
                      ))}
                  </tbody>
                </table>

                <p className="note">
                  BLE presence indicates smartphone detection, not independent
                  identity verification. Demo records are illustrative.
                </p>
              </section>
            </>
          )}

          {page === "Live Tracking" && (
            <section className="panel">
              <h3>Fleet tracking</h3>
              <p>
                Illustrative route map. Live GPS requires a valid backend GPS
                response.
              </p>
              <div className="maparea tall">
                <div className="routepath"></div>
                {buses.map((b, i) => (
                  <button
                    className={"marker m" + i}
                    key={b.id}
                    onClick={() => act(b.id + " selected")}
                  >
                    <Bus size={15} />
                    {b.id}
                  </button>
                ))}
              </div>
            </section>
          )}

          {page === "Buses & Routes" && (
            <section className="panel">
              <div className="panelhead">
                <h3>Bus fleet</h3>
                <input
                  className="input"
                  value={search}
                  onChange={(e) => Q(e.target.value)}
                  placeholder="Search buses/routes"
                />
              </div>

              <table>
                <thead>
                  <tr>
                    <th>BUS</th>
                    <th>ROUTE</th>
                    <th>DRIVER</th>
                    <th>PASSENGERS</th>
                    <th>SPEED</th>
                    <th>ETA</th>
                    <th>STATUS</th>
                  </tr>
                </thead>
                <tbody>
                  {buses
                    .filter((b) =>
                      (b.id + b.route + b.driver)
                        .toLowerCase()
                        .includes(search.toLowerCase())
                    )
                    .map((b) => (
                      <tr key={b.id}>
                        <td>{b.id}</td>
                        <td>{b.route}</td>
                        <td>{b.driver}</td>
                        <td>
                          {b.students}/{b.capacity}
                        </td>
                        <td>{b.speed} km/h</td>
                        <td>{b.eta} min</td>
                        <td>{b.status}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </section>
          )}

          {page === "Network Health" && (
            <>
              <div className="metrics">
                <Metric
                  icon={Wifi}
                  title="Driver network"
                  value={fallback ? "Weak" : "Good"}
                  sub="Primary source"
                />
                <Metric
                  icon={Network}
                  title="GPS source"
                  value={fallback ? "Student phone" : "Driver phone"}
                  sub="Demo state"
                />
                <Metric
                  icon={Activity}
                  title="Source availability"
                  value="2"
                  sub="Illustrative"
                />
              </div>

              <section className="panel">
                <h3>Network fallback architecture</h3>

                <div className="flow">
                  <div>
                    📱
                    <b>Driver phone</b>
                    <small>Primary GPS + BLE</small>
                  </div>
                  <strong>→</strong>
                  <div>
                    ☁️
                    <b>Flask backend</b>
                    <small>Validate and store</small>
                  </div>
                  <strong>←</strong>
                  <div>
                    📲
                    <b>Student phone</b>
                    <small>Own GPS + own internet</small>
                  </div>
                </div>

                <button
                  className="primary"
                  onClick={() => {
                    F(!fallback);
                    act(
                      fallback
                        ? "Driver source restored (demo)"
                        : "Student GPS source selected (demo)"
                    );
                  }}
                >
                  {fallback
                    ? "Restore driver source"
                    : "Simulate weak driver network"}
                </button>

                <p className="note">
                  This changes only the demo display; no real phone source
                  switching occurs.
                </p>
              </section>
            </>
          )}

          {page === "ETA Intelligence" && (
            <section className="panel">
              <h3>ETA intelligence · SB-101</h3>
              <div className="bigeta">
                12 <small>minutes</small>
              </div>
              <Info label="Current GPS" value="Demo coordinate" />
              <Info label="Recent movement" value="34 km/h sample" />
              <Info
                label="Historical trip data"
                value="Not verified in demo"
              />
              <Info label="Route progress" value="Illustrative" />
              <p className="note">
                Do not treat this sample ETA as a validated prediction. A real
                estimate should use current GPS, route distance and available
                historical trip data.
              </p>
            </section>
          )}

          {page === "Alerts & SOS" && (
            <section className="panel">
              <div className="panelhead">
                <h3>Alerts & emergency center</h3>
                <button
                  className="danger"
                  onClick={() => {
                    E(!sos);
                    act(sos ? "Demo SOS resolved" : "Demo SOS triggered");
                  }}
                >
                  <ShieldAlert size={16} />
                  {sos ? "Resolve demo SOS" : "Trigger demo SOS"}
                </button>
              </div>

              {sos && (
                <div className="sos">
                  ⚠ DEMO SOS ACTIVE · SB-103 · Simulated only; no emergency
                  service contacted.
                </div>
              )}

              <Info
                label="Proximity"
                value="SB-101 approaching Kaup"
              />
              <Info
                label="Network warning"
                value="SB-103 driver network weak"
              />
              <Info
                label="Attendance event"
                value="Student presence recorded"
              />
              <Info
                label="Route deviation"
                value="Illustrative warning"
              />
            </section>
          )}

          {["Trip History", "Reports"].includes(page) && (
            <section className="panel">
              <h3>{page}</h3>
              <p>
                Reports and trip history require verified backend endpoints.
                These sample figures are illustrative.
              </p>

              <div className="metrics">
                <Metric
                  icon={Clock3}
                  title="Average delay"
                  value="4.2 min"
                  sub="Sample only"
                />
                <Metric
                  icon={Network}
                  title="Network availability"
                  value="94%"
                  sub="Sample only"
                />
                <Metric
                  icon={Users}
                  title="Avg. presence"
                  value="34/40"
                  sub="Sample only"
                />
              </div>
            </section>
          )}

          <footer>
            © 2026 SmartBus · SMVITM Bantakal <span>{apiStatus}</span>
          </footer>
        </section>
      </main>

      {notice && (
        <div className="toast">
          <CheckCircle2 size={18} />
          {notice}
        </div>
      )}
    </div>
  );
}

function Metric({
  icon: Icon,
  title,
  value,
  sub,
}: {
  icon: any;
  title: string;
  value: string;
  sub: string;
}) {
  return (
    <div className="metric">
      <div className="metricicon">
        <Icon size={18} />
      </div>
      <small>{title}</small>
      <b>{value}</b>
      <span>{sub}</span>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="info">
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}