from tools.files_write import write_file

def main():
    path = "output/test_agent_note.txt"
    content = "Привет, это первая заметка, сохранённая через files.write()."
    result = write_file(path, content)
    print(result)

if __name__ == "__main__":
    main()

