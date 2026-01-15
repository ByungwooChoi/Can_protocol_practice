import sys

def parse_log_verbose(filename):
    print(f"--- Detailed ISO-TP Parsing: {filename} ---")
    print(f"{'CAN ID':<8} | {'Type':<4} | {'Info / Payload'}")
    print("-" * 60)

    buffers = {} 

    with open(filename, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) < 4 or '[' not in parts[2]: continue
            
            can_id_hex = parts[1]
            can_id = int(can_id_hex, 16)
            data = [int(b, 16) for b in parts[3:]]
            
            # PCI (Protocol Control Information) 분석
            pci_type = data[0] >> 4
            
            # --- Type 0: Single Frame ---
            if pci_type == 0:
                length = data[0] & 0x0F
                msg = bytearray(data[1:1+length]).decode(errors='replace')
                print(f"0x{can_id_hex:<6} | SF   | Msg: {msg}")
            
            # --- Type 1: First Frame ---
            elif pci_type == 1:
                total_len = ((data[0] & 0x0F) << 8) + data[1]
                print(f"0x{can_id_hex:<6} | FF   | Start Multi-Frame (Total: {total_len} bytes)")
                
                # 버퍼 시작 (데이터 수집용)
                buffers[can_id] = {'data': bytearray(data[2:]), 'total_len': total_len, 'seq': 1}
            
            # --- Type 2: Consecutive Frame ---
            elif pci_type == 2:
                seq_num = data[0] & 0x0F
                print(f"0x{can_id_hex:<6} | CF   | Sequence: {seq_num}")
                
                # 데이터 조립 로직
                if can_id in buffers:
                    buffers[can_id]['data'].extend(data[1:])
                    buffers[can_id]['seq'] = (buffers[can_id]['seq'] + 1) % 16
                    
                    # 다 모였는지 확인
                    current_len = len(buffers[can_id]['data'])
                    target_len = buffers[can_id]['total_len']
                    
                    if current_len >= target_len:
                        final_msg = buffers[can_id]['data'][:target_len].decode(errors='replace')
                        print(f"{' ' * 11}└──> [COMPLETE] : {final_msg}")
                        del buffers[can_id]

            # --- Type 3: Flow Control ---
            elif pci_type == 3:
                fs_map = {0: 'CTS (Continue)', 1: 'Wait', 2: 'Overflow'}
                fs = data[0] & 0x0F # Flow Status
                print(f"0x{can_id_hex:<6} | FC   | Status: {fs_map.get(fs, 'Unknown')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 log_parser_verbose.py <logfile>")
    else:
        parse_log_verbose(sys.argv[1])