import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def run_analytics():
    db_file = "warpbot_logs.db"
    
    try:
        conn = sqlite3.connect(db_file)
        # We only need timestamp, user_id, and username for these stats
        df = pd.read_sql_query("SELECT timestamp, user_id, username FROM ask_logs", conn)
        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")
        return

    if df.empty:
        print("No data found in database yet.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # TEXT STATS
    total_queries = len(df)
    unique_users = df['user_id'].nunique()
    
    # Get top 3 most active users
    top_users = df['username'].value_counts().head(3)

    print("-" * 30)
    print(f"📊 WARPBOT ANALYTICS")
    print("-" * 30)
    print(f"Total Queries:       {total_queries}")
    print(f"Unique Users:        {unique_users}")
    print("-" * 30)
    print("🏆 Top Active Users:")
    for user, count in top_users.items():
        print(f"  - {user}: {count} queries")
    print("-" * 30)

    # PLOTTING
    plt.style.use('bmh')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Group by Date and count
    daily_activity = df.set_index('timestamp').resample('D').count()['user_id']
    
    ax1.plot(daily_activity.index, daily_activity.values, marker='o', linestyle='-', color='#4245A0', linewidth=2)
    ax1.set_title('Queries per Day')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Number of Queries')
    ax1.grid(True)
    # Format date on X axis to be readable
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

    hourly_activity = df['timestamp'].dt.hour.value_counts().sort_index()
    hourly_activity = hourly_activity.reindex(range(24), fill_value=0)

    ax2.bar(hourly_activity.index, hourly_activity.values, color='#ff6b6b', alpha=0.8)
    ax2.set_title('Activity by Hour of Day (Local Time)')
    ax2.set_xlabel('Hour (24h format)')
    ax2.set_xticks(range(0, 24, 2)) # Show label every 2 hours
    ax2.set_ylabel('Total Queries')

    plt.tight_layout()
    print("📈 Opening graphs window...")
    plt.show()

if __name__ == "__main__":
    run_analytics()
