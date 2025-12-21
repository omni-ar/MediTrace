import sqlite3

def clean_database():
    db_path = "meditrace.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("🧹 Cleaning database...")

    # 1. Wo IDs nikalo jo "Augmentin 625 Duo" ki hain (Inhe bachana hai)
    drug_name_to_keep = "Augmentin 625 Duo"
    
    cursor.execute("SELECT id FROM drugs WHERE drug_name = ?", (drug_name_to_keep,))
    ids_to_keep = [row[0] for row in cursor.fetchall()]

    if not ids_to_keep:
        print(f"❌ Error: '{drug_name_to_keep}' database mein mila hi nahi! Kuch delete nahi kiya.")
        return

    print(f"✅ Found {len(ids_to_keep)} units of '{drug_name_to_keep}' to keep.")

    # Convert list to tuple for SQL query
    # Logic: Agar 1 item hai to simple bracket (1), agar zyada hain to tuple (1,2,3)
    if len(ids_to_keep) == 1:
        ids_tuple = f"({ids_to_keep[0]})"
    else:
        ids_tuple = str(tuple(ids_to_keep))

    # 2. Supply Chain Table se baaki sab delete karo
    cursor.execute(f"DELETE FROM supply_chain WHERE drug_id NOT IN {ids_tuple}")
    print(f"🗑️ Deleted unrelated Supply Chain events.")

    # 3. Drugs Table se baaki sab delete karo
    cursor.execute(f"DELETE FROM drugs WHERE id NOT IN {ids_tuple}")
    print(f"🗑️ Deleted unrelated Drugs.")

    # 4. (Optional) Ledger table agar banayi hai toh
    try:
        cursor.execute(f"DELETE FROM ledger WHERE drug_id NOT IN {ids_tuple}")
        print(f"🗑️ Deleted unrelated Ledger blocks.")
    except:
        pass

    conn.commit()
    conn.close()
    print("✨ Database Cleanup Complete! Only Augmentin remains.")

if __name__ == "__main__":
    clean_database()