CREATE TABLE IF NOT EXISTS flags (
  id integer primary key autoincrement,
  name TEXT,
  flag TEXT,
  method INTEGER,
  public TEXT,
  private TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP );