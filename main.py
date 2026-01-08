def main():
    print("File Type Identification: Version 0.1 (2024-06-01)")
    print("This program identifies file types based on their magic numbers.")
    print("Type 'exit' to quit the program.")
    print("-----------------------------------------------------")

    while True:
        file_path = input("Enter the file path (or type 'exit' to quit): ")
        if file_path.lower() == 'exit':
            print("Exiting the program...")
            break

        try:
            with open(file_path, 'rb') as file:
                magic_number = file.read(4)
                file_type = identify_file_type(magic_number)
                print(f"File Type: {file_type}")
        except FileNotFoundError:
            print("Error: File not found. Please check the path and try again.")
        except Exception as e:
            print(f"An error occurred: {e}")

def identify_file_type(magic_number):
    magic_dict = {
        b'\x89PNG': 'PNG Image',
        b'\xFF\xD8\xFF\xE0': 'JPEG Image',
        b'GIF8': 'GIF Image',
        b'%PDF': 'PDF Document',
        b'PK\x03\x04': 'ZIP Archive',
        b'Rar!': 'RAR Archive',
        b'\x7FELF': 'ELF Executable'
    }
    return magic_dict.get(magic_number, 'Unknown File Type')

main()