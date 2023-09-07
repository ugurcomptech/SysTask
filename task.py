import psutil
import tabulate
import time
import matplotlib.pyplot as plt
from collections import deque
import logging 
import csv
import platform

logging.basicConfig(filename='task_manager.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def list_processes():
    processes = []

    for process in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
        process_info = process.info
        processes.append([
            process_info['pid'],
            process_info['name'],
            f"{process_info['cpu_percent']:.2f}%",
            f"{process_info['memory_info'].rss / (1024 * 1024):.2f} MB",
            process_info['status']
        ])

    table = tabulate.tabulate(processes, headers=['PID', 'İşlem Adı', 'CPU Kullanımı', 'Bellek Kullanımı', 'Durum'], tablefmt='pretty')
    print(table)

def list_services():
    services = []

    for service in psutil.win_service_iter():
        try:
            service_name = service.name()
            service_status = service.status()
            service_display_name = service.display_name()
            services.append([service_name, service_status, service_display_name])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            logging.error(f"Hata: {service_name} hizmetini alırken bir hata oluştu.")  # Yeni: Hata günlüğüne kaydet

    table = tabulate.tabulate(services, headers=['Servis Adı', 'Durum', 'Görünen Ad'], tablefmt='pretty')
    print(table)

def show_performance():
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    memory_info = psutil.virtual_memory()

    print("CPU Kullanımı (%):")
    for i, core in enumerate(cpu_percent):
        print(f"Çekirdek {i}: {core:.2f}%")

    print(f"Toplam Bellek Kullanımı: {memory_info.percent:.2f}%")

    # Yeni: Performans bilgilerini günlüğe kaydet
    logging.info(f"CPU Kullanımı: {cpu_percent}")
    logging.info(f"Bellek Kullanımı: {memory_info.percent}")

def kill_process_by_pid(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()
        print(f"Süreç ({process.name()}) başarıyla sonlandırıldı.")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        print("Belirtilen süreç ID'si geçersiz veya sonlandırılamıyor.")

def search_process_by_name(name):  # Ekledik: Süreç adına göre arama
    processes = []

    for process in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
        process_info = process.info
        if name.lower() in process_info['name'].lower():  # Küçük/kapalı harf karşılaştırması
            processes.append([
                process_info['pid'],
                process_info['name'],
                f"{process_info['cpu_percent']:.2f}%",
                f"{process_info['memory_info'].rss / (1024 * 1024):.2f} MB",
                process_info['status']
            ])

    if processes:
        table = tabulate.tabulate(processes, headers=['PID', 'İşlem Adı', 'CPU Kullanımı', 'Bellek Kullanımı', 'Durum'], tablefmt='pretty')
        print(table)
    else:
        print(f"{name} adında bir süreç bulunamadı.")

def monitor_performance(interval, duration):  # Ekledik: Performans izleme süresi ve aralığı
    for _ in range(int(duration / interval)):
        show_performance()
        time.sleep(interval)


def export_process_data_to_csv():
    processes = []
    for process in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
        process_info = process.info
        processes.append([
            process_info['pid'],
            process_info['name'],
            f"{process_info['cpu_percent']:.2f}%",
            f"{process_info['memory_info'].rss / (1024 * 1024):.2f} MB",
            process_info['status']
        ])

    with open('processes.csv', 'w', newline='') as csvfile:
        fieldnames = ['PID', 'İşlem Adı', 'CPU Kullanımı', 'Bellek Kullanımı', 'Durum']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for process in processes:
            writer.writerow({'PID': process[0], 'İşlem Adı': process[1], 'CPU Kullanımı': process[2], 'Bellek Kullanımı': process[3], 'Durum': process[4]})

def import_process_data_from_csv():
    processes = []
    try:
        with open('processes.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                processes.append([row['PID'], row['İşlem Adı'], row['CPU Kullanımı'], row['Bellek Kullanımı'], row['Durum']])
    except FileNotFoundError:
        print("CSV dosyası bulunamadı.")

    table = tabulate.tabulate(processes, headers=['PID', 'İşlem Adı', 'CPU Kullanımı', 'Bellek Kullanımı', 'Durum'], tablefmt='pretty')
    print(table)

def show_system_info():
    system_info = {
        'İşletim Sistemi': platform.system(),
        'İşletim Sistemi Sürümü': platform.release(),
        'CPU Modeli': platform.processor(),
        'Toplam Bellek (GB)': psutil.virtual_memory().total / (1024**3)
    }

    print("Sistem Bilgileri:")
    for key, value in system_info.items():
        print(f"{key}: {value}")


while True:
    print("Gelişmiş Görev Yöneticisi")
    print("---------------------")
    print("1. Tüm süreçleri listele")
    print("2. Belirli süreci adına göre ara")
    print("3. Tüm servisleri listele")
    print("4. Sistem performansını göster")
    print("5. Performansı izle")
    print("6. Süreç sonlandır (PID ile)")
    print("7. Sistem Bilgilerini Görüntüle")
    print("0. Çıkış")

    choice = input("Seçiminizi girin: ")

    if choice == "1":
        list_processes()
    elif choice == "2":
        name = input("Aramak istediğiniz sürecin adını girin: ")
        search_process_by_name(name)
    elif choice == "3":
        list_services()
    elif choice == "4":
        show_performance()
    elif choice == "5":
        interval = float(input("İzleme aralığını (saniye cinsinden) girin: "))
        duration = float(input("İzleme süresini (saniye cinsinden) girin: "))
        monitor_performance(interval, duration)
    elif choice == "6":
        pid = input("Sonlandırmak istediğiniz sürecin PID'sini girin: ")
        if pid.isdigit():
            kill_process_by_pid(int(pid))
        else:
            print("Geçersiz PID. Tam sayı girin.")
    elif choice == "7":
        show_system_info()
    elif choice == "0":
        break
    else:
        print("Geçersiz seçenek. Tekrar deneyin.")
