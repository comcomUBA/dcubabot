from models import init_db, Listable
from handlers.db import get_session

def revive_all_groups():
    init_db()
    
    with get_session() as session:
        # Find groups that have a chat_id but are not validated
        dead_groups = session.query(Listable).filter(Listable.chat_id != None, Listable.validated == False).all()
        
        print(f"Found {len(dead_groups)} groups to revive.")
        for group in dead_groups:
            print(f"Reviving: {group.name} (Chat ID: {group.chat_id})")
            group.validated = True
            
    print("All groups have been revived. If any group is truly dead, the next cron job will handle it properly.")

if __name__ == "__main__":
    revive_all_groups()