from src.rag_lab.service import ask


def main() -> None:
    result = ask("修改任务后，为什么需要让Redis缓存失效？")
    print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    main()