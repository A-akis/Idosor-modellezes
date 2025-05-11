import numpy as np
from datetime import datetime
import sqlite3
def get_regressors_matrix(df, m, N, index_col = 'index'):
    index = df[index_col].values.reshape([N,1])
    trend = np.concatenate([np.ones([N,1]), index], axis = 1)
    season = np.zeros([N,1])
    for i in range(m):
        # print(i)
        season = np.concatenate([season, np.cos((2*np.pi*(i+1)*index)/12), np.sin((2*np.pi*(i+1)*index)/12)], axis = 1)
    season = season[:,1:]
    return np.concatenate([trend, season], axis = 1)


class SignalGenerator:
    def __init__(self, 
                 intercept=10, 
                 slope=0,
                 a1_day=1.0, 
                 a1_evening=1.4,
                 b1=0.5, 
                 period_minutes=30,
                 noise_std=0.3):
        self.intercept = intercept
        self.slope = slope
        self.a1_day = a1_day
        self.a1_evening = a1_evening
        self.b1 = b1
        self.period_minutes = period_minutes
        self.noise_std = noise_std

    def _generate_single(self, t_minute):
        # Choose a1 based on time of day
        a1 = self.a1_day if t_minute % 1440 < 1080 else self.a1_evening

        omega = 2 * np.pi / self.period_minutes
        periodic = a1 * np.sin(omega * t_minute) + self.b1 * np.cos(omega * t_minute)
        noise = np.random.normal(0, self.noise_std)

        y = self.intercept + self.slope * t_minute + periodic + noise
        return y

    def __call__(self, t=None):
        if t is None:
            now = datetime.now()
            t_minute = now.hour * 60 + now.minute
            return self._generate_single(t_minute)
        elif isinstance(t, (list, np.ndarray, range)):
            return np.array([self._generate_single(tm) for tm in t])
        else:
            raise TypeError("t must be None, a list, a numpy array, or a range.")

#%%
def init_db(db_path='signals.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS signal_data (
            timestamp TEXT PRIMARY KEY,
            t_minute INTEGER,
            signal REAL
        )
    ''')
    conn.commit()
    conn.close()

#%%
