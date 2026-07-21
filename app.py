import requests
import pandas as pd
import matplotlib.pyplot as plt

# data.go.th = พอร์ทัลข้อมูลเปิดของรัฐบาลไทย เรียกผ่าน API ได้ฟรี
RESOURCE_ID = "38b840af-f119-4bea-9208-66188da5cc1b"  # ราคาสินค้าเกษตรที่เกษตรกรขายได้ (รายเดือน)
URL = "https://data.go.th/api/3/action/datastore_search"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}  # ช่วยไม่ให้ถูกบล็อกว่าเป็นบอท

# 1) ขอข้อมูลทั้งชุดจาก API (raise_for_status + ตรวจ error ให้เห็นสาเหตุชัด)
resp = requests.get(URL, params={"resource_id": RESOURCE_ID, "limit": 5000},
                    headers=HEADERS, timeout=30)
resp.raise_for_status()
recs = resp.json()["result"]["records"]
ราคา = pd.DataFrame(recs).rename(columns={"เกษตรสำคัญบึงกาฬ": "สินค้า", "ค่า": "ราคา"})
ราคา["ราคา"] = pd.to_numeric(ราคา["ราคา"], errors="coerce")

# 2) เลือกผลไม้/พืชที่สนใจ (ทุเรียน = พืชคู่ของคอร์สนี้)
สินค้าที่ดู = ["ทุเรียนหมอนทองคละ", "เงาะโรงเรียนคละ", "กล้วยหอมทองขนาดคละ",
              "สับปะรดโรงงาน", "มันสำปะหลังคละ", "ยางแผ่นดิบชั้น 3"]

ปีล่าสุด = int(ราคา["ปี"].max())
เดือนเรียง = ["ม.ค.","ก.พ.","มี.ค.","เม.ย.","พ.ค.","มิ.ย.","ก.ค.","ส.ค.","ก.ย.","ต.ค.","พ.ย.","ธ.ค."]

ปีนี้ = ราคา[(ราคา["ปี"] == ปีล่าสุด) & (ราคา["สินค้า"].isin(สินค้าที่ดู))].copy()
ปีนี้["เดือน"] = pd.Categorical(ปีนี้["เดือน"], categories=เดือนเรียง, ordered=True)
ตาราง = ปีนี้.pivot_table(index="เดือน", columns="สินค้า", values="ราคา", observed=False)

# 3) แสดงราคาเดือนล่าสุดที่มีข้อมูล
เดือนล่าสุด = ตาราง.dropna(how="all").index[-1]
print(f"ราคาสินค้าเกษตรล่าสุด: {เดือนล่าสุด} {ปีล่าสุด} (บาท/กก.)")
print(ตาราง.loc[เดือนล่าสุด].dropna().sort_values(ascending=False).to_string())

# 4) กราฟราคารายเดือนของปีล่าสุด
fig, ax = plt.subplots(figsize=(11, 5))
for col in ตาราง.columns:
    ax.plot(ตาราง.index.astype(str), ตาราง[col], marker="o", label=col)
ax.set_title(f"ราคาสินค้าเกษตรรายเดือน ปี {ปีล่าสุด} (จ.บึงกาฬ)")
ax.set_ylabel("บาท/กก.")
ax.legend(fontsize=8, ncol=2)
plt.tight_layout()
plt.show()