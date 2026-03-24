export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  toolCalls?: ToolCallInfo[];
}

export interface ToolCallInfo {
  name: string;
  arguments: Record<string, unknown>;
  result?: Record<string, unknown>;
  error?: string;
}

export interface VIPPLResult {
  tier: string | null;
  nominal_volume: number;
  weighted_volume: number;
  ggr: number;
  casino_ggr: number;
  sportsbook_ggr: number;
  ops_costs: {
    casino_ops: number;
    sportsbook_ops: number;
    total: number;
  };
  bonuses: {
    level_up: number;
    reload: number;
    weekly: number;
    monthly: number;
    lossback_standard: number;
    lossback_discretionary: number;
    total: number;
  };
  ngr_before_promos: number;
  affiliate_cost: number;
  ngr_after_affiliate: number;
  promos: { total: number };
  ngr_after_promos: number;
  margins: {
    ggr_pct_of_nominal: number;
    ngr_pct_of_ggr: number;
    total_cost_pct_of_ggr: number;
  };
}

export interface CompanyPLMonth {
  month: number;
  total_wagers: number;
  ggr: {
    total: number;
    pragmatic: number;
    evo: number;
    ogs: number;
    sportsbook: number;
  };
  ngr: number;
  profit_before_opex: number;
  profit_after_opex: number;
}

export interface CompanyPLProjection {
  months: CompanyPLMonth[];
  cumulative: {
    wagers: number;
    ggr: number;
    ngr: number;
    profit_after_opex: number;
  };
  breakeven_month: number | null;
}

export interface Scenario {
  id: string;
  name: string;
  chat_history: ChatMessage[];
  calc_results: Record<string, unknown>[];
  created_at: string;
}
