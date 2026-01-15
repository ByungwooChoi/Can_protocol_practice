import isotp
import argparse
import time

def run_client(target_name, rx_id, tx_id, message):
    print(f"[*] Client connecting to {target_name} (Send: {hex(tx_id)}, Listen: {hex(rx_id)})...")
    
    addr = isotp.Address(isotp.AddressingMode.Normal_11bits, rxid=rx_id, txid=tx_id)
    s = isotp.socket()
    s.bind("vcan0", address=addr)
    
    try:
        # 요청 전송
        print(f"[*] Sending: {message}")
        s.send(message.encode('utf-8'))
        
        # 응답 대기
        resp = s.recv()
        if resp:
            print(f"[*] Response from {target_name}: {resp.decode()}")
        else:
            print("[!] No response received.")
            
    finally:
        s.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=str, required=True, help="Target Name (Engine/Camera)")
    parser.add_argument("--rx-id", type=lambda x: int(x, 0), required=True) # 내 수신 ID (상대방의 TX)
    parser.add_argument("--tx-id", type=lambda x: int(x, 0), required=True) # 내 송신 ID (상대방의 RX)
    parser.add_argument("--msg", type=str, required=True)
    args = parser.parse_args()
    
    run_client(args.target, args.rx_id, args.tx_id, args.msg)