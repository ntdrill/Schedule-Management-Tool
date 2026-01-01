from supabase import create_client, Client

url: str = "https://nonrlrdalfefykzborvm.supabase.co"
key: str = "sb_publishable_3H0ns8nZBmJuAhOgCUd0gw_sTURYilU"

try:
    print(f"Connecting to: {url}")
    # クライアントの初期化
    supabase: Client = create_client(url, key)
    print("Supabase client initialized.")
    
    # 接続テスト
    print("Testing connection...")
    try:
        # まだテーブルがないためエラーになる可能性がありますが、
        # 認証エラー(401)か、テーブルなしエラー(404/PGRST200)かで接続可否を判断します
        response = supabase.table("symbols").select("*").limit(1).execute()
        print(f"Connection successful! Response: {response}")
    except Exception as query_err:
        print(f"Query executed. Result/Error: {query_err}")
        
        err_str = str(query_err)
        if "401" in err_str or "JWT" in err_str:
            print("Warning: Authentication failed. Key might be invalid.")
        else:
            print("Connection likely successful (Table 'symbols' probably does not exist yet).")

except Exception as e:
    print(f"Connection failed: {e}")
