import time
import nextcord as discrd
import functions
import datetime
import re


async def send_action_message(args):
    # args = {"bot": "", "guild_id": "", "user_name": "", "user_id": "", "action_type": "", "moderator": "", "reason": "", "seconds": ""}
    if args["action_type"] in ["Ban", "Timeout", "Kick", "Unban", "Remove Timeout"]:
        log_channel_id = functions.preferences.gpdb.get_pref(
            "modlog_channel", args["guild_id"])
    else:
        log_channel_id = functions.preferences.gpdb.get_pref(
            "warnlog_channel", args["guild_id"])
    log_channel = args["bot"].get_channel(log_channel_id)
    human_readable_time = 0

    if log_channel:
        guild_infractions = functions.preferences.gpdb.db['infractions'].find_one(
            {'guild_id': args['guild_id']})
        if guild_infractions:
            if args["action_type"] in ["Ban", "Timeout", "Kick", "Unban", "Remove Timeout"]:
                field_name = 'modactions'
            else:
                field_name = 'warns'
            if field_name not in guild_infractions:
                guild_infractions[field_name] = []
            case_no = max(
                (infraction['case_no']
                 for infraction in guild_infractions[field_name]),
                default=0
            ) + 1
        else:
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

        message = await log_channel.send(action_message)

        # Store infraction information in database
        infraction = {
            'case_no': case_no,
            'guild_id': args['guild_id'],
            'user_id': args['user_id'],
            'action_type': args['action_type'],
            'moderator': str(args['moderator']),
            'reason': args.get('reason', ''),
            'timestamp': datetime.datetime.utcnow(),
            'message_id': message.id
        }
        if 'seconds' in args:
            infraction['duration'] = human_readable_time
            infraction['until'] = datetime.datetime.utcnow(
            ) + datetime.timedelta(seconds=args['seconds'])

        if args['action_type'] == 'Warn':
            field_name = 'warns'
        else:
            field_name = 'modactions'

        functions.preferences.gpdb.db['infractions'].update_one(
            {'guild_id': args['guild_id']},
            {'$push': {field_name: infraction}},
            upsert=True
        )

    return human_readable_time


async def edit_action_message(args, caseNo, newReason, option):
    if option == "infraction":
        log_channel_id = functions.preferences.gpdb.get_pref(
            "modlog_channel", args["guild_id"])
    else:
        log_channel_id = functions.preferences.gpdb.get_pref(
            "warnlog_channel", args["guild_id"])
    log_channel = args["bot"].get_channel(log_channel_id)

    if option == "infraction":
        field_name = 'modactions'
    else:
        field_name = 'warns'
    guild_infractions = functions.preferences.gpdb.db['infractions'].find_one(
        {'guild_id': args['guild_id']})
    infraction = next(
        (inf for inf in guild_infractions[field_name] if inf['case_no'] == caseNo), None)

    if not infraction:
        await args["interaction"].response.send_message(f"Unable to find case number {caseNo}")
        return False

    infraction['reason'] = newReason
    functions.preferences.gpdb.db['infractions'].update_one(
        {'guild_id': args['guild_id'], f'{field_name}.case_no': caseNo},
        {'$set': {f'{field_name}.$.reason': newReason}}
    )

    log_message = await log_channel.fetch_message(infraction['message_id'])

    if "Reason: " in log_message.content:
        new_content = re.sub(r'(?<=Reason: ).+',
                             newReason, log_message.content)
        await log_message.edit(content=new_content)
        return True
    else:
        await args["interaction"].response.send_message(f"The action message for case number {caseNo} does not have a 'Reason' field.")
        return False
