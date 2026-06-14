import discord
from discord import app_commands
from discord.ext import commands, tasks
import requests
import uuid
import random
import os
import json
import threading
import asyncio
from flask import Flask, request as flask_request, jsonify

# --- ⚙️ Configuration ---
TOKEN = os.getenv('DISCORD_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 1284107691723067454))
EXTRA_ROLE_ID = 1512850411554345030
GACHA_COST = 1000

# --- 🎭 Rank & Group Config (1-255) ---
GROUPS_CONFIG = [{"group_id": 35646818, "ranks": {
    1: {"add": [1512850411554345030, 1512850409570566189, 1515205019522175098], "remove": []},
    2: {"add": [1512850408215679167], "remove": [1512850409570566189]},
    3: {"add": [1512850408215679167], "remove": [1512850409570566189]},
    4: {"add": [1512850408215679167], "remove": [1512850409570566189]},
    5: {"add": [1512850408215679167], "remove": [1512850409570566189]},
    6: {"add": [1512850408215679167], "remove": [1512850409570566189]},
    7: {"add": [1512850408215679167], "remove": [1512850409570566189]},
    8: {"add": [1512850406013665351], "remove": [1512850408215679167]},
    9: {"add": [1512850406013665351], "remove": [1512850409570566189]},
    10: {"add": [1512850406013665351], "remove": [1512850409570566189]},
    11: {"add": [1512850406013665351], "remove": [1512850409570566189]},
    12: {"add": [1512850402217955470], "remove": [1512850409570566189]},
    13: {"add": [1512850402217955470], "remove": [1512850409570566189]},
    14: {"add": [1512850402217955470], "remove": [1512850409570566189]},
    15: {"add": [1512850402217955470], "remove": [1512850409570566189]},
    16: {"add": [1512850287646347375], "remove": [1512850402217955470]},
    17: {"add": [1512850287646347375], "remove": [1512850409570566189]},
    18: {"add": [1512850287646347375], "remove": [1512850409570566189]},
    19: {"add": [1512850289336520855], "remove": [1512850402217955470]},
    20: {"add": [1512850289336520855], "remove": [1512850409570566189]},
    21: {"add": [1512850271192219779, 1515203999194812426, 1512850277630345267], "remove": [1512850409570566189]},
    22: {"add": [1512850271192219779, 1515203999194812426, 1512850277630345267], "remove": [1512850409570566189]},
    23: {"add": [1512850277630345267], "remove": [1512850409570566189]},
    24: {"add": [1512850289336520855], "remove": [1512850409570566189]},
    25: {"add": [1512850289336520855, 1512850259842302234], "remove": [1512850409570566189]},
    26: {"add": [1512850257761931305], "remove": [1512850409570566189]},
    27: {"add": [1512850274476228618, 1512850279132037130, 1512850277630345267], "remove": [1512850409570566189]},
    28: {"add": [1512850274476228618, 1512850262409084949, 1512850277630345267], "remove": [1512850409570566189]},
    30: {"add": [1515203999194812426, 1512850271192219779, 1512850277630345267], "remove": [1512850409570566189]},
    31: {"add": [1512850320647262519, 1512850322895278090, 1512850325487358044, 1512850290934681812], "remove": [1512850409570566189]},
    32: {"add": [1512850320647262519, 1512850322895278090, 1512850325487358044, 1512850290934681812], "remove": [1512850409570566189]},
    33: {"add": [1512850256185004155, 1512850290934681812, 1512850271192219779, 1515203999194812426], "remove": [1512850409570566189]},
    34: {"add": [1515203999194812426, 1512850271192219779, 1512850277630345267, 1512850290934681812], "remove": [1512850409570566189]},
    35: {"add": [1512850271192219779, 1512850277630345267, 1515203999194812426], "remove": [1512850409570566189]},
    36: {"add": [1512850269468229662], "remove": [1512850409570566189]},
    254: {"add": [1512850246592364744], "remove": [1512850409570566189]},
    255: {"add": [1512850246592364744], "remove": [1512850409570566189]},
}}]

RANK_NAMES = {
    1: "OR-1, PC", 2: "OR-D, PNCO", 3: "OR-3, CPL", 4: "OR-4, SGT",
    5: "OR-5, SSG", 6: "OR-6/OR-7, SFC", 7: "OR-8/OR-9, MSG", 8: "OF-D, PC",
    9: "OF-1a, LTP", 10: "1LT, CPT", 11: "OF-2, CPT", 12: "OF-3, MAJ", 
    13: "OF-4, LTC", 14: "OF-5, COL", 15: "OF-6, SRCOL", 16: "OF-7, PMG", 
    17: "OF-8, PLG", 18: "OF-9, GEN", 19: "MR", 20: "RH", 21: "OF-9, APC",
    22: "ER", 23: "OF-10, PG,", 24: "CH", 25: "HMQ", 26: "HMK", 27: "DPM",
    28: "PM", 30: "OF-9, APC" , 31: "OF-9, DIG", 32: "OF-9, IG", 33: "OF-9, PA", 
    34: "OF-9, DCG", 35: "OF-9, CG", 36: "OF-9, MI", 254: "DEV", 255: "ไก่เกิน"
}

# --- 🖥️ Database ---
DB_FILE = 'users_db.json'
users_db = {}
active_sessions = {}

def load_db():
    global users_db
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f: users_db = json.load(f)
        except: users_db = {}

def save_db():
    with open(DB_FILE, 'w', encoding='utf-8') as f: json.dump(users_db, f, indent=4)

load_db()

# --- 🛡️ Sync Logic ---
async def perform_sync_silent(guild, discord_id, roblox_username):
    try:
        member = await guild.fetch_member(int(discord_id))
        res_id = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [roblox_username]}, timeout=5 ).json()
        r_id = res_id['data'][0]['id']
        res_groups = requests.get(f"https://groups.roblox.com/v1/users/{r_id}/groups/roles", timeout=5 ).json()
        user_groups = {g['group']['id']: g['role']['rank'] for g in res_groups.get('data', [])}
        rank_id = user_groups.get(GROUPS_CONFIG[0]['group_id'], 0)
        rank_name = RANK_NAMES.get(rank_id, f"Rank-{rank_id}")
        new_nick = (f"{rank_name} | {roblox_username}")[:32]
        if guild.owner_id != member.id:
            try: await member.edit(nick=new_nick)
            except: pass
        roles_to_add = []
        for config in GROUPS_CONFIG:
            g_id = config['group_id']
            if g_id in user_groups:
                u_rank = user_groups[g_id]
                if u_rank in config['ranks']:
                    for rid in config['ranks'][u_rank].get("add", []):
                        role = guild.get_role(rid)
                        if role: roles_to_add.append(role)
        extra_role = guild.get_role(EXTRA_ROLE_ID)
        if extra_role: roles_to_add.append(extra_role)
        if roles_to_add: await member.add_roles(*roles_to_add)
        return True
    except: return False

# --- 📝 UI Views ---
class VerificationModal(discord.ui.Modal, title='ยืนยันตัวตน Roblox'):
    username = discord.ui.TextInput(label='ชื่อใน Roblox', placeholder='ใส่ชื่อตัวละครของคุณที่นี่...')
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        u_name = self.username.value.strip()
        try:
            res_user = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [u_name]}, timeout=5 ).json()
            if not res_user.get('data'): return await interaction.followup.send("❌ ไม่พบชื่อ", ephemeral=True)
            code = str(uuid.uuid4())[:8]
            active_sessions[str(interaction.user.id)] = {"roblox_username": u_name, "verification_code": code}
            await interaction.followup.send(f"✅ รหัสของคุณคือ: **{code}**\nนำไปใส่ในเกมแล้วกลับมาอัปเดตยศครับ", ephemeral=True)
        except: await interaction.followup.send("❌ ระบบขัดข้อง", ephemeral=True)

class ManagementView(discord.ui.View):
    def __init__(self, roblox_username):
        super().__init__(timeout=None)
        self.roblox_username = roblox_username
    @discord.ui.button(label="🔄 อัปเดตยศล่าสุด", style=discord.ButtonStyle.primary, custom_id="btn_sync_v4")
    async def update_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await perform_sync_silent(interaction.guild, interaction.user.id, self.roblox_username)
        await interaction.followup.send(f"✅ อัปเดตยศสำหรับ **{self.roblox_username}** สำเร็จ!", ephemeral=True)
    @discord.ui.button(label="⚙️ ผูกไอดีใหม่", style=discord.ButtonStyle.secondary, custom_id="btn_reverify_v4")
    async def reverify_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VerificationModal())

class VerifyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="📝 ยืนยันตัวตน / จัดการไอดี", style=discord.ButtonStyle.success, custom_id="btn_verify_v4")
    async def verify_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        d_id = str(interaction.user.id)
        if d_id in users_db:
            username = users_db[d_id].get("roblox_username", "Unknown")
            embed = discord.Embed(title="⚙️ จัดการบัญชีของคุณ", description=f"ปัจจุบันคุณผูกไว้กับไอดี: **{username}**", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed, view=ManagementView(username), ephemeral=True)
        else: await interaction.response.send_modal(VerificationModal())

class GachaView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="เช็ค EXP", style=discord.ButtonStyle.primary, custom_id="btn_xp_v4")
    async def xp_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        xp = users_db.get(str(interaction.user.id), {}).get("xp", 0)
        await interaction.response.send_message(f"✨ EXP ของคุณคือ: `{xp:,}`", ephemeral=True)
    @discord.ui.button(label="สุ่ม Role", style=discord.ButtonStyle.success, custom_id="btn_roll_v4")
    async def roll_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        d_id = str(interaction.user.id)
        if d_id not in users_db: return await interaction.response.send_message("❌ ต้องยืนยันตัวตนก่อน", ephemeral=True)
        if users_db[d_id].get("xp", 0) < GACHA_COST: return await interaction.response.send_message("❌ EXP ไม่พอ", ephemeral=True)
        users_db[d_id]["xp"] -= GACHA_COST
        save_db()
        if random.random() < 0.5: await interaction.response.send_message("🎖️ ยินดีด้วย! คุณได้รับยศ **ร้อยตรี**", ephemeral=True)
        else: await interaction.response.send_message("🧂 เกลือจ้า!", ephemeral=True)

# --- 🤖 Bot ---
class MyBot(commands.Bot):
    def __init__(self): super().__init__(command_prefix="!", intents=discord.Intents.all())
    async def setup_hook(self):
        self.add_view(VerifyView()); self.add_view(GachaView()); self.add_view(ManagementView(""))
        await self.tree.sync()

bot = MyBot()

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    if not xp_task.is_running(): xp_task.start()

@bot.tree.command(name="setup_verify")
async def setup_verify(interaction: discord.Interaction):
    if interaction.user.id != ADMIN_ID: return
    await interaction.channel.send(embed=discord.Embed(title="🛡️ ระบบยืนยันตัวตน", color=discord.Color.blue()), view=VerifyView())
    await interaction.response.send_message("✅ ติดตั้งแผงยืนยันสำเร็จ", ephemeral=True)

@bot.tree.command(name="setup_gacha")
async def setup_gacha(interaction: discord.Interaction):
    if interaction.user.id != ADMIN_ID: return
    await interaction.channel.send(embed=discord.Embed(title="🎰 ระบบสุ่มยศ", description=f"ใช้ {GACHA_COST:,} EXP ต่อการสุ่ม 1 ครั้ง", color=discord.Color.gold()), view=GachaView())
    await interaction.response.send_message("✅ ติดตั้งแผงกาชาสำเร็จ", ephemeral=True)

@tasks.loop(minutes=1.0)
async def xp_task():
    for guild in bot.guilds:
        for member in guild.members:
            if member.voice and not member.bot and str(member.id) in users_db:
                users_db[str(member.id)]["xp"] += 35
                save_db()

# --- 🖥️ API ---
app = Flask(__name__)

@app.route("/check_code", methods=["POST"])
def check_code():
    data = flask_request.json
    code = data.get("verification_code")
    for d_id, s in active_sessions.items():
        if s["verification_code"] == code:
            future = asyncio.run_coroutine_threadsafe(bot.fetch_user(int(d_id)), bot.loop)
            try:
                user = future.result(timeout=10)
                return jsonify({"success": True, "discord_name": str(user)}), 200
            except: break
    return jsonify({"success": False}), 400

@app.route("/complete_verification", methods=["POST"])
def complete_verification():
    data = flask_request.json
    u, c = data.get("roblox_username"), data.get("verification_code")
    for d_id, s in active_sessions.items():
        if s["roblox_username"] == u and s["verification_code"] == c:
            users_db[d_id] = {"roblox_username": u, "xp": users_db.get(d_id, {}).get("xp", 0)}
            save_db(); del active_sessions[d_id]
            if bot.guilds: bot.loop.create_task(perform_sync_silent(bot.guilds[0], d_id, u))
            return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True).start()
    bot.run(TOKEN)
