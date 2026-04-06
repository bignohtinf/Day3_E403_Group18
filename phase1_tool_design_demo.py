from src.tools.registry import build_registry


def main() -> None:
    registry = build_registry()

    print("=== Phase 1: Tool Design Demo ===")
    print("Discovered tools:")
    for spec in registry.list_specs():
        print(f"- {spec['name']}: {spec['description']}")

    print("\nScenario sample calls (Smart E-commerce Assistant):")
    print("[check_stock] iphone 15")
    print(registry.execute("check_stock", "iphone 15"))

    print("\n[get_discount] WINNER")
    print(registry.execute("get_discount", "WINNER"))

    print("\n[calc_shipping] 2.0, Hanoi")
    print(registry.execute("calc_shipping", "2.0, Hanoi"))

    print("\n[web_search] iPhone 15 price Vietnam")
    print(registry.execute("web_search", "iPhone 15 price Vietnam"))


if __name__ == "__main__":
    main()
