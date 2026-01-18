with open('src/api/chat_api.py', 'r', encoding='utf-8') as f:
    content = f.read()
    print("Checking for int(conversation_id)...")
    if 'int(conversation_id)' in content:
        import re
        matches = re.finditer(r'int\(conversation_id\)', content)
        for match in matches:
            # Find the line number
            line_start = content.rfind('\n', 0, match.start()) + 1
            line_end = content.find('\n', match.start())
            if line_end == -1:
                line_end = len(content)
            line_number = content[:match.start()].count('\n') + 1
            print(f"Found at line {line_number}: {content[line_start:line_end]}")
    else:
        print("No int(conversation_id) found in the file")
        
    print("\nChecking for the get_conversation_messages endpoint...")
    import re
    pattern = r'async def get_conversation_messages.*?session, int\(conversation_id\)'
    matches = re.findall(pattern, content, re.DOTALL)
    if matches:
        print("Found get_conversation_messages with int(conversation_id):")
        for match in matches:
            print(repr(match))
    else:
        print("No get_conversation_messages with int(conversation_id) found")
        
    # Also check for any remaining int(conversation_id) in the get_conversation_messages function
    # Find the function and check its content
    func_pattern = r'async def get_conversation_messages.*?session\.close\(\)'
    functions = re.findall(func_pattern, content, re.DOTALL)
    for func in functions:
        if 'int(conversation_id)' in func:
            print(f"Function contains int(conversation_id): {func[:100]}...")