import asyncio
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from google import genai

from perception.afferens_client import AfferensClient
from perception.scene_builder import SceneBuilder

load_dotenv()

async def run_student_monitor():
    ai_client = genai.Client() if os.getenv("GEMINI_API_KEY") else None
    
    total_study_seconds = 0
    total_distracted_seconds = 0
    distraction_count = 0
    was_distracted_last_frame = False
    start_time = time.time()
    
    log_filename = "study_session_log.txt"
    
    print(f"=== 🎓 Student Focus Monitoring Session Initialized ===")
    print(f"Saving permanent history logs to: {log_filename}")
    print("Press Ctrl+C to end the study session and generate your report.\n")
    
    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(f"\n=== NEW STUDY SESSION STARTED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    async with AfferensClient() as client:
        try:
            while True:
                perception = await client.get_vision()
                
                # FIX 1: If the dashboard node is stopped or offline, pause tracking gracefully
                if perception.get("status") == 404 or "error" in perception:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] 💤 [PAUSED] Dashboard node offline. Waiting for stream connection...", end="\r")
                    await asyncio.sleep(2.0)
                    continue
                
                scene = SceneBuilder.build(perception)
                
                # Evaluate State
                if not scene.person or scene.phone:
                    current_distracted = True
                    total_distracted_seconds += 1
                    current_state_str = "❌ DISTRACTED"
                else:
                    current_distracted = False
                    total_study_seconds += 1
                    current_state_str = "📝 STUDYING"
                
                # Track state transitions
                alert_triggered = False
                if current_distracted and not was_distracted_last_frame:
                    distraction_count += 1
                    alert_triggered = True
                
                was_distracted_last_frame = current_distracted
                
                # Append row to history log file
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_entry = f"[{timestamp}] State: {current_state_str} | Objects: {scene.objects}"
                if alert_triggered:
                    log_entry += " -> ⚠️ ALERT: Student switched to distracted state!"
                
                with open(log_filename, "a", encoding="utf-8") as f:
                    f.write(log_entry + "\n")
                
                print(log_entry)
                await asyncio.sleep(1.0)
                
        except KeyboardInterrupt:
            end_time = time.time()
            total_session_time = int(end_time - start_time)
            
            summary_stats = (
                f"\n=== SESSION SUMMARY ===\n"
                f"Total Duration: {total_session_time} seconds\n"
                f"Active Study Time: {total_study_seconds} seconds\n"
                f"Distracted Time: {total_distracted_seconds} seconds\n"
                f"Total Distraction Incidents: {distraction_count}\n"
                f"=======================\n"
            )
            
            with open(log_filename, "a", encoding="utf-8") as f:
                f.write(summary_stats)
                
            print("\n🛑 Session ended. Raw metrics appended to log file.")
            
            if ai_client and total_study_seconds > 0:
                print("🤖 Querying Gemini for your coach evaluation report...")
                report_prompt = (
                    f"You are an empathetic, analytical student productivity coach.\n"
                    f"Analyze these study metrics:\n{summary_stats}\n"
                    f"Provide a summary evaluation and 2 practical tips to stay focused."
                )
                try:
                    response = ai_client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=report_prompt
                    )
                    report_text = f"\n✨ === GEMINI COACHING REPORT === ✨\n{response.text}\n"
                    
                    with open(log_filename, "a", encoding="utf-8") as f:
                        f.write(report_text)
                        
                    print(report_text)
                except Exception as e:
                    print(f"Could not reach Gemini: {e}")

if __name__ == "__main__":
    asyncio.run(run_student_monitor())