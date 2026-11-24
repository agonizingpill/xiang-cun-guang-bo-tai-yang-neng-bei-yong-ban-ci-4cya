        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "电池换表与交割",
  "module": "换表交割",
  "caption": "换表交割",
  "detail": "交割前取旧表、交割小时起取新表。读数未补齐也可先审签，同一旧表只认先审签的一份。",
  "path": "/meter_switches",
  "columns": [
    {
      "name": "code",
      "label": "换表单"
    },
    {
      "name": "old_meter",
      "label": "旧表"
    },
    {
      "name": "new_meter",
      "label": "新表"
    },
    {
      "name": "handover_hour",
      "label": "交割小时"
    },
    {
      "name": "approved",
      "label": "已审签"
    },
    {
      "name": "approved_by",
      "label": "审签人"
    }
  ],
  "layout": "stack",
  "view": "table",
  "actions": [
    {
      "name": "submit_switch",
      "label": "提交换表交割",
      "path": "/meter_switches/submit-switch",
      "fields": [
        {
          "name": "code",
          "label": "换表单号",
          "kind": "text",
          "initial": "MS-24"
        },
        {
          "name": "old_meter",
          "label": "旧表",
          "kind": "text",
          "initial": "BAT-04"
        },
        {
          "name": "new_meter",
          "label": "新表",
          "kind": "text",
          "initial": "BAT-11"
        },
        {
          "name": "handover_hour",
          "label": "交割小时",
          "kind": "int",
          "initial": 24
        }
      ],
      "help": "交割前取旧表，交割小时起取新表。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "approve_switch",
      "label": "审签换表交割",
      "path": "/meter_switches/approve-switch",
      "fields": [
        {
          "name": "code",
          "label": "换表单号",
          "kind": "text",
          "initial": "MS-24"
        }
      ],
      "help": "读数可后补；同一旧表同时提交多份时只认先审签的一份。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入"
    }
  ]
};

        export const {title} = page;
        export const key = "meter_switches";
        export async function render(root, role) {
          await workspace(root, role, page);

        }
