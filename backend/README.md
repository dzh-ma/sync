---
author: dzh-ma
date: 2025-01-02
---

# Report Generation

1. **Navigate to root of the app**
```bash
cd app/
```

2. **Use MongoDB Compass to pick the `id` field of the `user` collection, whose report will be generated**

3. **Ensure data is validated for report generation**
```bash
python inspect_data.py <id>
```

4. **Generate report for the specified user**
```bash
python generate_report.py --user-id <user> --format <pdf/csv> --days <int>
```

5. **Navigate to generated report**
```bash
cd utils/report/generated_reports/
```

---
