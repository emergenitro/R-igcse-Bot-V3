import time

import nextcord as discrd

import functions

async def send_action_message(args):
    # args = {"bot": "", "guild_id": "", "user_name": "", "user_id": "", "action_type": "", "moderator": "", "reason": "", "seconds": ""}
    ban_msg_channel = args["bot"].get_channel(functions.preferences.gpdb.get_pref("modlog_channel", args["guild_id"]))
    human_readable_time = 0

    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = (int("".join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1)
        except:
            case_no = 1

        if "reason" in args and args["reason"]:
            if "seconds" in args and args["seconds"]:
                seconds = args["seconds"]
                human_readable_time = f"{seconds // 86400}d {(seconds % 86400) // 3600}h {(seconds % 3600) // 60}m {seconds % 60}s"

                action_message = f"""Case #{case_no} | [{args["action_type"]}]
Username: {str(args["user_name"])} ({args["user_id"]})
Moderator: {args["moderator"]}
Reason: {args["reason"]}
Duration: {human_readable_time}
Until: <t:{int(time.time()) + seconds}> (<t:{int(time.time()) + seconds}:R>)"""
            else:
                action_message = f"""Case #{case_no} | [{args["action_type"]}]
Username: {str(args["user_name"])} ({args["user_id"]})
Moderator: {args["moderator"]}
Reason: {args["reason"]}"""
        else:
            action_message = f"""Case #{case_no} | [{args["action_type"]}]
Username: {str(args["user_name"])} ({args["user_id"]})
Moderator: {args["moderator"]}"""

        await ban_msg_channel.send(action_message)

        return human_readable_time