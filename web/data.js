export const dictionary = {
  user: {
    神経: ['副交感優位', '交感優位', 'バランス'],
    行動: ['太極拳', '軽い散歩', '掃除', '深呼吸', 'メッセージ返信'],
    想起: ['ゆっくり動くと頭が冴える', '呼吸を整える', '創作のアイデア'],
    目標: ['解離感解消', '過覚醒の回復', '集中維持'],
    筋肉: ['弛緩', 'normal', '過緊張'],
    栄養: ['電解質補給', 'クエン酸カプセル'],
    脈拍: ['安定', '高'],
  },
  environment: {
    清潔度: ['高', '中', '低'],
    換気: ['良好', 'やや不足', '不足'],
    照明: ['明るい', '自然光', '暗い'],
    温度: ['快適', 'やや低い', 'やや高い'],
    整理整頓: ['整っている', '一部散らかり', '散らかっている'],
  },
  social: {
    最終対人接触: ['今日', '昨日', '3日以上前'],
    対人ストレス: ['低', '中', '高'],
    サポート感: ['十分', '不足'],
  },
};

export const criticalStates = [
  { id: 'over_arousal', label: '過覚醒', priority: 'urgent' },
  { id: 'mold_depression', label: 'カビ鬱', priority: 'high' },
  { id: 'fatigue_desire', label: '疲労性欲', priority: 'medium' },
  { id: 'social_isolation', label: '孤独感増大', priority: 'medium' },
];

export const taskTemplates = [
  {
    id: 'taichi_session',
    title: '太極拳セッション',
    icon: '🧘',
    category: 'exercise',
    defaultDurationMinutes: 40,
    color: '#10b981',
    description:
      '神経系を副交感優位に誘導し、筋肉の弛緩と解離感の解消を狙う全身運動。',
    stateSignature: {
      Before: {
        user: {
          神経: '副交感優位',
          筋肉: '弛緩',
        },
      },
      After: {
        user: {
          目標: '解離感解消',
          行動: '太極拳',
        },
      },
    },
    preconditions: {
      user: {
        神経: ['副交感優位', 'バランス'],
        筋肉: ['弛緩', 'normal'],
      },
    },
    criticalStateRelation: {
      helpsRecover: ['過覚醒'],
      prevents: ['疲労性欲'],
    },
  },
  {
    id: 'deep_cleaning',
    title: '環境整備（浴室掃除）',
    icon: '🧽',
    category: 'housekeeping',
    defaultDurationMinutes: 60,
    color: '#f97316',
    description:
      '湿度とカビリスクを下げ、環境の清潔度を高める集中清掃タスク。',
    stateSignature: {
      Before: {
        environment: {
          清潔度: '低',
          換気: '不足',
        },
      },
      After: {
        environment: {
          清潔度: '高',
          換気: '良好',
          整理整頓: '整っている',
        },
        user: {
          行動: '掃除',
          想起: 'ゆっくり動くと頭が冴える',
        },
      },
    },
    preconditions: {
      user: {
        神経: ['バランス', '副交感優位'],
      },
      environment: {
        温度: ['快適', 'やや低い'],
      },
    },
    criticalStateRelation: {
      prevents: ['カビ鬱'],
    },
  },
  {
    id: 'message_check_in',
    title: 'メッセージでの近況共有',
    icon: '💬',
    category: 'communication',
    defaultDurationMinutes: 20,
    color: '#6366f1',
    description:
      '信頼できる相手と連絡を取り合い、社会的サポート感を高めるコミュニケーション。',
    stateSignature: {
      Before: {
        social: {
          最終対人接触: '3日以上前',
          サポート感: '不足',
        },
      },
      After: {
        social: {
          最終対人接触: '今日',
          サポート感: '十分',
          対人ストレス: '低',
        },
        user: {
          想起: '呼吸を整える',
        },
      },
    },
    preconditions: {
      user: {
        神経: ['副交感優位', 'バランス'],
      },
      social: {
        対人ストレス: ['低', '中'],
      },
    },
    criticalStateRelation: {
      helpsRecover: ['孤独感増大'],
    },
  },
  {
    id: 'recovery_breathing',
    title: '30回の呼吸セッション',
    icon: '🌬️',
    category: 'recovery',
    defaultDurationMinutes: 10,
    color: '#0ea5e9',
    description:
      '過覚醒の兆候に対して交感神経優位を鎮める緊急リカバリータスク。',
    stateSignature: {
      Before: {
        user: {
          神経: '交感優位',
          脈拍: '高',
        },
      },
      After: {
        user: {
          神経: '副交感優位',
          脈拍: '安定',
          行動: '深呼吸',
        },
      },
    },
    preconditions: {
      user: {
        神経: ['交感優位', 'バランス'],
      },
    },
    criticalStateRelation: {
      helpsRecover: ['過覚醒'],
    },
  },
];

export const initialState = {
  user: {
    神経: 'バランス',
    行動: '軽い散歩',
    想起: '呼吸を整える',
    目標: '集中維持',
    筋肉: 'normal',
    栄養: '電解質補給',
    脈拍: '安定',
  },
  environment: {
    清潔度: '中',
    換気: 'やや不足',
    照明: '自然光',
    温度: '快適',
    整理整頓: '一部散らかり',
  },
  social: {
    最終対人接触: '昨日',
    対人ストレス: '中',
    サポート感: '不足',
  },
};

export const categories = [
  { id: 'exercise', label: '運動' },
  { id: 'housekeeping', label: '家事' },
  { id: 'communication', label: 'コミュニケーション' },
  { id: 'recovery', label: 'リカバリー' },
];
