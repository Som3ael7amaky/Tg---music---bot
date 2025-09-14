from pyrogram import Client
import asyncio

# توليد Session String علشان تشتغل بالمكالمات
# لازم تكون مجهز API_ID و API_HASH من https://my.telegram.org

async def main():
    print("أدخل API_ID:")
    api_id = int(input().strip())
    print("أدخل API_HASH:")
    api_hash = input().strip()

    async with Client(":memory:", api_id=api_id, api_hash=api_hash) as app:
        session_string = await app.export_session_string()
        print("\n✅ Session String اتولد بنجاح:\n")
        print(session_string)
        print("\n⚠️ انسخ الـ Session وحطه في config.py أو في Secrets في الاستضافة.")

if __name__ == "__main__":
    asyncio.run(main())