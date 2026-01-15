import isotp
import time
import argparse
import logging

def run_ecu(interface, rx_id, tx_id, role):
    # 로깅 설정 (Role에 따라 이름 변경)
    logging.basicConfig(level=logging.INFO, format=f'[{role.upper()}] %(asctime)s - %(message)s')
    logger = logging.getLogger(role)

    addr = isotp.Address(isotp.AddressingMode.Normal_11bits, rxid=rx_id, txid=tx_id)
    s = isotp.socket()
    s.bind(interface, address=addr)
    
    logger.info(f"ECU Started on {interface} | RX: {hex(rx_id)}, TX: {hex(tx_id)}")

    try:
        while True:
            req = s.recv() # Blocking Wait
            if req:
                msg = req.decode(errors='ignore')
                logger.info(f"Request Received: {msg}")
                
                # 역할별 응답 로직
                resp_msg = ""
                if role == "engine":
                    if "RPM" in msg:
                        resp_msg = "Current RPM: 2500, Oil Temp: 90C. Engine is running smoothly."
                    else:
                        resp_msg = "Engine: Unknown Command"
                
                elif role == "camera":
                    if "Obstacle" in msg:
                        resp_msg = "[WARNING] Obstacle Detected! Distance: 30cm. Be careful!"
                    else:
                        resp_msg = "Camera: Unknown Command"

                s.send(resp_msg.encode('utf-8'))
                logger.info(f"Sent Response: {resp_msg}")
                
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        s.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", type=str, required=True, help="engine or camera")
    parser.add_argument("--rx-id", type=lambda x: int(x, 0), required=True)
    parser.add_argument("--tx-id", type=lambda x: int(x, 0), required=True)
    args = parser.parse_args()
    
    run_ecu("vcan0", args.rx_id, args.tx_id, args.role)