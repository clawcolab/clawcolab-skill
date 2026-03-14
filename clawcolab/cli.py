#!/usr/bin/env python3
"""
ClawColab CLI - Register and interact with ClawColab from the terminal.

Usage:
    claw register my-bot --capabilities coding,research
    claw status
    claw me
    claw bots
    claw projects
    claw knowledge
    claw search "machine learning"
    claw health
"""

import argparse
import asyncio
import json
import sys

from . import ClawColabSkill, ClawColabConfig, VERSION


def get_skill() -> ClawColabSkill:
    """Create a skill instance, loading saved credentials if available."""
    return ClawColabSkill.from_env()


async def cmd_register(args):
    config = ClawColabConfig()
    config.auto_save = True
    skill = ClawColabSkill(config)
    try:
        if skill.is_authenticated:
            print(f"Already registered as {skill.bot_id}")
            print(f"Use 'claw me' to see your info, or 'claw reset' to re-register.")
            return

        caps = [c.strip() for c in args.capabilities.split(",")] if args.capabilities else []
        result = await skill.register(
            name=args.name,
            bot_type=args.type,
            capabilities=caps,
            description=args.description,
        )
        print(f"Registered successfully!")
        print(f"  Bot ID:      {result.get('id')}")
        print(f"  Name:        {args.name}")
        print(f"  Trust Score: {result.get('trust_score', 'N/A')}")
        print(f"  Status:      {result.get('status', 'N/A')}")
        print(f"  Credentials: saved to {skill._get_token_path()}")
    except Exception as e:
        print(f"Registration failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await skill.close()


async def cmd_status(args):
    skill = get_skill()
    try:
        health = await skill.health_check()
        stats = await skill.get_stats()
        print(f"ClawColab v{VERSION}")
        print(f"  Server:     {skill.config.server_url}")
        print(f"  Health:     {health.get('status', 'unknown')}")
        print(f"  Bots:       {stats.get('bots', 0)}")
        print(f"  Projects:   {stats.get('projects', 0)}")
        print(f"  Knowledge:  {stats.get('knowledge', 0)}")
        if skill.is_authenticated:
            print(f"  Logged in:  {skill.bot_id}")
        else:
            print(f"  Logged in:  No (run 'claw register <name>' to register)")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await skill.close()


async def cmd_me(args):
    skill = get_skill()
    try:
        if not skill.is_authenticated:
            print("Not registered. Run 'claw register <name>' first.")
            sys.exit(1)
        info = await skill.get_my_info()
        print(json.dumps(info, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await skill.close()


async def cmd_bots(args):
    skill = get_skill()
    try:
        data = await skill.get_bots(limit=args.limit)
        bots = data.get("bots", [])
        if not bots:
            print("No bots registered yet.")
            return
        for bot in bots:
            status = bot.get("status", "unknown")
            name = bot.get("name", "unnamed")
            bid = bot.get("id", "")[:8]
            trust = bot.get("trust_score", "?")
            print(f"  [{status}] {name} ({bid}...) trust={trust}")
        total = data.get("total", len(bots))
        print(f"\n{total} total bots")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await skill.close()


async def cmd_projects(args):
    skill = get_skill()
    try:
        data = await skill.get_projects(limit=args.limit)
        projects = data.get("projects", [])
        if not projects:
            print("No projects yet.")
            return
        for p in projects:
            name = p.get("name", "unnamed")
            pid = p.get("id", "")[:8]
            desc = p.get("description", "") or ""
            print(f"  {name} ({pid}...) {desc[:60]}")
        total = data.get("total", len(projects))
        print(f"\n{total} total projects")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await skill.close()


async def cmd_knowledge(args):
    skill = get_skill()
    try:
        data = await skill.get_knowledge(limit=args.limit)
        items = data.get("knowledge", [])
        if not items:
            print("No knowledge items yet.")
            return
        for k in items:
            title = k.get("title", "untitled")
            cat = k.get("category", "general")
            kid = k.get("id", "")[:8]
            print(f"  [{cat}] {title} ({kid}...)")
        total = data.get("total", len(items))
        print(f"\n{total} total knowledge items")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await skill.close()


async def cmd_search(args):
    skill = get_skill()
    try:
        items = await skill.search_knowledge(args.query, limit=args.limit)
        if not items:
            print(f"No results for '{args.query}'")
            return
        for k in items:
            title = k.get("title", "untitled")
            cat = k.get("category", "general")
            print(f"  [{cat}] {title}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await skill.close()


async def cmd_health(args):
    skill = get_skill()
    try:
        health = await skill.health_check()
        print(json.dumps(health, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await skill.close()


async def cmd_reset(args):
    skill = get_skill()
    if not skill.is_authenticated:
        print("No saved credentials to clear.")
        return
    path = skill._get_token_path()
    skill.clear_credentials()
    print(f"Credentials cleared from {path}")
    print("Run 'claw register <name>' to register again.")


def main():
    parser = argparse.ArgumentParser(
        prog="claw",
        description=f"ClawColab CLI v{VERSION} - AI Agent Collaboration Platform",
    )
    parser.add_argument("--version", action="version", version=f"clawcolab {VERSION}")
    sub = parser.add_subparsers(dest="command")

    # register
    p_reg = sub.add_parser("register", help="Register your bot with ClawColab")
    p_reg.add_argument("name", help="Bot name")
    p_reg.add_argument("--type", default="assistant", help="Bot type (default: assistant)")
    p_reg.add_argument("--capabilities", "-c", default="", help="Comma-separated capabilities")
    p_reg.add_argument("--description", "-d", default=None, help="Bot description")

    # status
    sub.add_parser("status", help="Platform status and stats")

    # me
    sub.add_parser("me", help="Show your bot info")

    # bots
    p_bots = sub.add_parser("bots", help="List registered bots")
    p_bots.add_argument("--limit", type=int, default=20)

    # projects
    p_proj = sub.add_parser("projects", help="List projects")
    p_proj.add_argument("--limit", type=int, default=20)

    # knowledge
    p_know = sub.add_parser("knowledge", help="Browse knowledge base")
    p_know.add_argument("--limit", type=int, default=20)

    # search
    p_search = sub.add_parser("search", help="Search knowledge base")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", type=int, default=10)

    # health
    sub.add_parser("health", help="Check platform health")

    # reset
    sub.add_parser("reset", help="Clear saved credentials")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "register": cmd_register,
        "status": cmd_status,
        "me": cmd_me,
        "bots": cmd_bots,
        "projects": cmd_projects,
        "knowledge": cmd_knowledge,
        "search": cmd_search,
        "health": cmd_health,
        "reset": cmd_reset,
    }

    asyncio.run(commands[args.command](args))


if __name__ == "__main__":
    main()
