# <img src="assets/docs/header_green.png" width="370">

Pixelbot for Diablo 2 Resurrected. This project is for informational and educational purposes only.

## Getting started & Prerequisites
- D2R needs to be in English Language,
- Botty currently works with 720p D2R window (will be adjusted automatically on auto settings)

### 1) Graphics and Gameplay Settings

All settings will automatically be set when you execute `main.exe` and press the hotkey for "Adjust D2R settings" (default f9). It is not a 100% thing, in rare cases you might still have to fiddle around with your brightness. I suggest using the "Graphic Debugger" to verify your settings.
**Note**: Make sure that no other external programs adapt your graphics settings (HDR, Geforce Experience, etc.)

### 2) Supported builds

Check the documentation for **params.ini** further down. Different Sorc builds, Hammerdin, Barb, Trapsin are already implemented to different extents. It is quite straightforward to implement new classes. Give it a go if you like!

### 3) Start Location

Open up D2R and wait till you are at the hero selection screen. Make sure the char you running with is selected and will be in any of Act 3, 4 or 5 in the respective difficulty you set in the **params.ini** once the bot starts the game.

### 4) Start Botty

You can either run from python. Follow [development.md](development.md) for that. Or you download the a prebuilt release [here](https://github.com/aeon0/botty/releases) (the .rar file!). Start `main.exe` in the botty folder. Focus your D2R window and press the start key (default f11). You can always force stop botty with f12. Note: Botty will use the /nopickup command in the first game to avoid pickup up trash while traversing. This command will only allow item pickup when "show items" is active.

## Development

Check out the [development.md](development.md) docu for infos on how to build from source and details of the project structure and code.

## BNIP Pickit

Botty NIP (BNIP) is an extended version of Njaguar's Item Parser (NIP).
BNIP is compatible with NIP (with some minor exceptions as discussed below).

There is a default nip file that comes with botty called "default.nip" inside config folder, you can add your own nip files by putting them inside config/nip with a file extension of .nip. Creating your own nip file also turns off the default.nip.

We suggest you read the NIP guide if you are unfamiliar with NIP https://github.com/blizzhackers/pickits/blob/master/NipGuide.md

### New features in BNIP

Poison damage is no longer calculated, but is now read as it's raw value. Example: Adds 5-10 poison damage over 1 seconds can be picked with `[poisonmindam] == 5 && [poisonmaxdam] == 10`. "313 Poison Damage over 5 seconds" can be picked with `[poisonmindam] == 313` or  `[poisonmaxdam] == 313`.

`[allres]` is a thing now. example: `[type] == amulet && [quality] == unique # [allres] == 30` will pick up Mara's

`[idname]` can now be used for unique / set items. For example, `[idname] == thestoneofjordan` will pick up SoJ. Keep in mind, however, this forces the item to be ID'd so be careful if you want to keep unid items.

`[maxquantity]` is not supported (yet). You can leave those tags in but they'll do nothing.

If you have the discord webhook hooked up to alert you when the bot keeps items, you can suppress these alerts by adding a "@" in front of your expression.

@[type] == ring = no notification
[type] == ring = notification

## Graphic Debugger

To check if you graphic settings are good and if the bot would pick up items there is a **Graphic Debugger Mode**. Start botty and press F10 (Default key). This will open up a (mostly black) window. Start a game in D2R and go to A5. You should see some templates with blue circles detected and scores printed out to the console. To check item finding, throw some items of different types on the ground. The debug window should show the item names with black background. If you throw an item on the ground that should be picked up, it will have a red circle. The console will print out the scores for each item that would be picked up. Scores should be well above 0.9 for these items.</br>
<img src="assets/docs/graphic_debugger.png" width="900">

## params.ini

All botty configuration files are located in the __config__ folder. To ease the switch to new botty versions, you can also overwrite any of the .ini fields in a **custom.ini** file. When a new version of botty is released you just copy the file to the new version without having to port all your **params.ini** changes to the new version. Example:

```ini
; custom.ini - overwrites 2 params in the params.ini
[general]
name=MyCustomName

[routes]
order=run_pindle, run_eldritch
```

| [general]                | Descriptions              |
| --------------------     | --------------------------|
| difficulty               | Set to `normal` `nightmare` or `hell` for game difficulty. |
| name                     | Name used in terminal and discord messages. |
| randomize_runs           | Randomize the order of `[routes]` specified in `params.ini`. |
| saved_games_folder       | [Optional] Defaults to `~\Saved Games\Diablo II Resurrected`. Used to store configuration settings for `f9` / auto settings. |
| custom_loot_message_hook      | Add your message hook here (such as Discord channel) to get info about loot |
| custom_message_hook      | Add your message hook here (such as Discord channel) to get info about botty status updates, discord webhook is default. |
| discord_log_chicken      | Set to `1` to enable messages about bot chickens, `0` to disable. |
| discord_status_count     | Number of games between discord status messages being sent. Leave empty for no status reports. |
| message_api_type         | Which api to use to send botty messages.  Supports "generic_api" (basic discord), or "discord" (discord embeds with images). |
| break_length_m           | Break for `break_length_m` minutes every `max_runtime_before_break_m` minutes |
| max_runtime_before_break_m | ^ |
| d2r_path                 | [Optional] Path to `d2r.exe`. If not set, it will default to `C:\Program Files (x86)\Diablo II Resurrected\D2R.exe` when attempting to restart. |
| max_consecutive_fails    | Botty will stop making games if the number of consecutive fails reaches this max value. |
| max_game_length_s        | Max game length in seconds. Botty will attempt to stop whatever it's doing and try to restart a new game at specified interval. If this fails, botty will attempt to shut down D2R and Bnet. |
| restart_d2r_when_stuck   | Set to `1` and botty will attempt to restart d2r in the case that botty is unable to recover its state (e.g: game crash). |
| info_screenshots         | If `1`, the bot takes a screenshot with timestamp on every stuck / chicken / timeout / inventory full event. This is 1 by Default, so remember to clean up the folder every once in a while. |
| pickit_screenshots         | If `1`, the bot takes a screenshot with timestamp on every ground loot snapshot taken during pickit routine, can be useful for debugging. |
| loot_screenshots         | If `1`, the bot takes a screenshot with timestamp everytime he presses `show_items` button and saves it to `loot_screenshots` folder. Remember to clear them once in a while... |

| [routes]     | Descriptions                                                             |
| ------------ | ------------------------------------------------------------------------ |
| order        | List of runs botty should do. These will be run in the the order listed unless `randomize_runs` is set to 1. Possible runs: </br> run_trav, run_pindle, run_eldritch, run_eldritch_shenk, run_nihlathak (requires teleport), run_arcane (requires teleport), run_diablo (requires teleport, only hammardin)

| [char]             | Descriptions |
| ------------------ | -------------------------------------------------------------------------------------------------|
| type               | Build type. Currently only "sorceress" or "hammerdin" is supported |
| belt_rows          | Integer value of how many rows the char's belt has |
| casting_frames     | Depending on your char and fcr you will have a specific casting frame count. Check it here: https://diablo2.diablowiki.net/Breakpoints and fill in the right number. Determines how much delay there is after each teleport for example. If your system has some delay e.g. on vms, you might have to increase this value above the suggest value in the table! |
| cta_available      | 0: no cta available, 1: cta is available and should be used during prebuff |
| safer_routines    | Set to 1 to enable optional defensive maneuvers/etc during combat/runs at the cost of increased runtime (ex. hardcore players)
| num_loot_columns   | Number of columns in inventory used for loot (from left!). Remaining space can be used for charms |
| force_move         | Hotkey for "force move" |
| inventory_screen   | Hotkey to open inventory |
| potion1            | Hotkey to take potion in slot 1 |
| potion2            | Hotkey to take potion in slot 2 |
| potion3            | Hotkey to take potion in slot 3 |
| potion4            | Hotkey to take potion in slot 4 |
| show_belt          | Hotkey for "show belt" |
| show_items         | Hotkey for "show items" |
| stand_still        | Hotkey for "stand still". Note this can not be the default shift key as it would interfere with the merc healing routine |
| teleport           | Hotkey for teleport (set blank if your character can't teleport) |
| town_portal           | Hotkey for town portal |
| weapon_switch      | Hotkey for "weapon switch" (only needed if cta_available=1) |
| battle_order       | Hotkey for battle orders from cta (only needed if cta_available=1) |
| battle_command     | Hotkey for battle command from cta (only needed if cta_available=1) |
| stash_gold         | Bool value to stash gold each time when stashing items |
| use_merc           | Set to 1 for using merc. Set to 0 for not using merc (will not revive merc when dead), default = 1 |
| atk_len_arc        | Attack length for hdin/sorc fighting arcane  |
| atk_len_eldritch   | Attack length for hdin or number of attack sequences for sorc when fighting eldritch |
| atk_len_nihlathak   | Attack length for hdin or number of attack sequences for sorc when fighting nihlathak |
| atk_len_pindle     | Attack length for hdin or number of attack sequences for sorc when fighting pindle |
| atk_len_shenk      | Attack length for hdin or number of attack sequences for sorc when fighting shenk |
| atk_len_trav       | Attack length for hdin fighting trav (note this atk length will be applied in 4 different spots each) |
| atk_len_cs_trashmobs   | Attack length for hdin or number of attack sequences when fighting Trash Mobs in Chaos Sanctuary (Diablo) |
| atk_len_diablo_deseis   | Attack length for hdin or number of attack sequences when fighting Sealboss B "Lord De Seis" in Chaos Sanctuary (Diablo) |
| atk_len_diablo_infector   | Attack length for hdin or number of attack sequences when fighting Sealboss C "Infector of Souls" in Chaos Sanctuary (Diablo) |
| atk_len_diablo_vizier   | Attack length for hdin or number of attack sequences when fighting Sealboss A "Vizier of Chaos" in Chaos Sanctuary (Diablo) |
| atk_len_diablo   | Attack length for hdin or number of attack sequences when fighting Diablo in Chaos Sanctuary |
| cs_mob_detect | If 1, it will attempt to use holy freeze from merc / conviction aura / poison to detect nearby mobs to help speed-up CS run.
| cs_town_visits   | CURRENTLY BROKEN, LEAVE AT 0 FOR NOW |
| kill_cs_trash   | If 1, most Trash mob packs from Chaos Sancturay Entrance to Pentagram are cleared. If 0, the run starts at Pentagram and just kills Sealbosses & Diablo (default) |
| belt_hp_columns    | Number of belt columns for healing potions |
| belt_mp_columns    | Number of belt columns for mana potions |
| belt_rejuv_columns | Number of belt columns for rejuv potions |
| take_health_potion | Health percentage when healing potion will be used. e.g. 0.6 = 60% helath |
| take_mana_potion   | Mana percentage when mana potion will be used |
| take_rejuv_potion_health | Health percentag when rejuv potion will be used |
| take_rejuv_potion_mana   | Mana percentag when rejuv potion will be used |
| heal_merc          | Merc health percentage when giving healing potion to merc |
| heal_rejuv_merc    | Merc health percentage when giving rejuv potion to merc |
| chicken            | Will chicken (leave game) when player health percentage drops below set value, range 0 to 1. Set to 0 to not chicken. |
| merc_chicken       | Will chicken (leave game) when merc health percentage drops below set value, range 0 to 1. Set to 0 to not chicken. |
| enable_no_pickup   | When enabled, will type `/nopickup` into chat at game start, which can help reduce accidental pickups especially for walking characters. |
| fill_shared_stash_first | Fill stash tabs starting from right to left, filling personal stash last |
| gamble_items       | List of items to gamble when stash fills with gold. Leave blank to disable. Supported items currently include circlet, ring, coronet, talon, amulet
| open_chests        | Open up chests in some places. E.g. on dead ends of arcane. |
| pre_buff_every_run | 0: Will only prebuff on first run, 1: Will prebuff after each run/boss |
| runs_per_repair    | Force repair after `runs_per_repair` of runs. Set to 0 to repair only when needed. |
| runs_per_stash    | 0: Will only stash after intentional item pickup, 1+: Will force stash after # of runs set here (recommend at least 4 in case of accidental pickups) |
| sell_junk          | 0: Discard unwanted items by dropping them on ground. 1: Discard items by selling them at vendor. |

| [transmute]             | Descriptions |
| ------------------ | -------------------------------------------------------------------------------------------------|
| stash_destination | Stash tabs by priority to place the results of the transmute. Default: 3,2,1,0. (It means the result will be first placed in stash 3 untils it's full, then to stash 2, etc. 0 - personal tab)
| transmute         | Add any or all of `chipped, flawed, standard, flawless` to trasmute gems of these types |
| transmute_every_x_game               | How often to run transmute routine (currently transmutes flawless gems into perfect gems). Transmute routine depends on stashing routine it will only start after items stashing is done. E.g. so it could take more than X games to perform transmutes if there were no items to stash at the time. Default: 20  |

### Builds
| [sorceress]   | Descriptions                                                                  |
| ------------- | ----------------------------------------------------------------------------- |
| frozen_armor  | Optional Hotkey for frozen armor (or any of the other armors)                 |
| energy_shield | Optional Hotkey for energy shield                                             |
| thunder_storm | Optional Hotkey for thunder storm                                             |
| static_field | Optional Hotkey for static field                                      |
| telekinesis | Optional Hotkey for telekinesis                                      |

| [light_sorc]  | Descriptions                                                                  |
| ------------- | ----------------------------------------------------------------------------- |
| chain_lightning | Optional Hotkey for chain_lightning (must be bound to left skill)           |
| lightning     | Required Hotkey for lightning (must be bound to right skill)                  |
| frozen_orb     | Optional Hotkey for frozen orb (must be bound to right skill)                  |

| [blizz_sorc]  | Descriptions                                                                  |
| ------------- | ----------------------------------------------------------------------------- |
| blizzard      | Required Hotkey for Blizzard (must be bound to right skill)                   |
| ice_blast     | Optional Hotkey for ice_blast (must be bound to left skill)                   |

| [nova_sorc]   | Descriptions                                                                  |
| ------------- | ----------------------------------------------------------------------------- |
| nova          | Required Hotkey for Nova (must be bound to right skill)                       |

| [hydra_sorc]  | Descriptions                                                                  |
| ------------- | ----------------------------------------------------------------------------- |
| alt_attack     | Required Hotkey for any alternate attacking skill. Fireball,Lightning,Frozen Orb, etc. (must be bound to right skill)                             |
| hydra         | Required Hotkey for Hydra (must be bound to right skill)                      |

| [paladin]    | Descriptions                                                                        |
| -------------- | ----------------------------------------------------------------------------------- |
| cleansing      | Optional Hotkey for Cleansing                                                       |
| holy_shield    | Required Hotkey for Holy Shield                                                     |
| redemption     | Optional Hotkey for Redemption                                                      |
| vigor          | Optional Hotkey for Vigor                                                           |

| [fohdin]    | Descriptions                                                                        |
| -------------- | ----------------------------------------------------------------------------------- |
| blessed_hammer | Hotkey for Blessed Hammer. (Optional. Bind to left skill)                  |
| concentration  | Hotkey for Concentration                                                   |
| conviction  | Hotkey for Conviction                                                   |
| foh  | Hotkey for Fist of Heavens (Required)                                                   |
| holy_bolt  | Hotkey for Holy Bolt (Required)                                                   |


| [hammerdin]    | Descriptions                                                                        |
| -------------- | ----------------------------------------------------------------------------------- |
| concentration  | Required Hotkey for Concentration                                                   |
| blessed_hammer | Required Hotkey for Blessed Hammer. (must be bound to left skill!)                  |

| [trapsin]    | Descriptions                                                                          |
| -------------- | ----------------------------------------------------------------------------------- |
| burst_of_speed | Optional Hotkey for Burst of Speed                                                  |
| death_sentry   | Required Hotkey for Death Sentry                                                    |
| fade           | Optional Hotkey for Fade                                                            |
| lightning_sentry | Required Hotkey for Lightning Sentry                                              |
| shadow_warrior | Optional Hotkey for Shadow Warrior                                                  |
| skill_left     | Optional Hotkey for Left Skill                                                      |

| [barbarian]    | Descriptions                                                                        |
| -------------- | ----------------------------------------------------------------------------------- |
| cry_frequency  | Time in seconds between each cast of war_cry. Set to 0.0 if max fcr should be used  |
| find_item      | Optional Hotkey for Find Item                                                       |
| leap           | Required Hotkey for Leap                                                            |
| shout          | Required Hotkey for Shout                                                           |
| war_cry        | Required Hotkey for War Cry                                                         |

| [Necro]        | Descriptions                                                                        |
| -------------- | ----------------------------------------------------------------------------------- |
| skill_left     | Required Hotkey for attack (bonespear/teeth)                                        |
| bone_armor     | Required Hotkey for Bone Armor                                                      |
| clay_golem     | Required Hotkey for Clay Golem                                                      |
| raise_skeleton | Required Hotkey for Raise Skeleton                                                  |
| amp_dmg        | Required Hotkey for Amplify Damage                                                  |
| corpse_explosion | Required Hotkey Corpse Explosion                                                  |
| raise_revive   | Required Hotkey revive                                                              |
| damage_scaling   | Adjusts time spent casting attack skills. Ex: 2 will cast twice as long           |
| clear_pindle_packs | Clears mobs before pindle                                                       |

| [advanced_options]   | Descriptions                                                          |
| -------------------- | --------------------------------------------------------------------- |
