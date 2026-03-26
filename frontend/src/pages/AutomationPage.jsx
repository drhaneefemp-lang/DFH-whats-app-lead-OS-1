import { useState } from 'react';
import {
  Lightning,
  Plus,
  Trash,
  PencilSimple,
  ToggleLeft,
  ToggleRight,
  CaretDown,
  CaretUp,
  Clock,
  CheckCircle,
  XCircle,
  Play,
  Pause
} from '@phosphor-icons/react';
import { format } from 'date-fns';
import {
  useAutomationRules,
  useAutomationMeta,
  useSchedulerStatus,
  useAgentsForAutomation
} from '../hooks/useAutomation';

const TRIGGER_ICONS = {
  new_message: '💬',
  new_lead: '🆕',
  no_reply: '⏰',
  lead_status_change: '🔄',
  scheduled: '📅'
};

const ACTION_LABELS = {
  send_message: 'Send Message',
  assign_lead: 'Assign Lead',
  update_status: 'Update Status',
  add_tag: 'Add Tag',
  send_template: 'Send Template'
};

const AutomationPage = () => {
  const { rules, loading, createRule, updateRule, deleteRule, toggleRule, refresh } = useAutomationRules();
  const { triggers, actions } = useAutomationMeta();
  const { status: schedulerStatus } = useSchedulerStatus();
  const { agents } = useAgentsForAutomation();
  
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [expandedRule, setExpandedRule] = useState(null);

  const handleToggle = async (ruleId) => {
    try {
      await toggleRule(ruleId);
    } catch (err) {
      console.error('Failed to toggle rule:', err);
    }
  };

  const handleDelete = async (ruleId) => {
    if (window.confirm('Are you sure you want to delete this rule?')) {
      try {
        await deleteRule(ruleId);
      } catch (err) {
        console.error('Failed to delete rule:', err);
      }
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    try {
      return format(new Date(dateString), 'MMM d, HH:mm');
    } catch {
      return 'Never';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50" data-testid="automation-page">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Lightning size={28} weight="fill" className="text-green-500" />
            <div>
              <h1 className="text-xl font-bold text-gray-900 font-[Chivo]">Automation</h1>
              <p className="text-xs text-gray-500">Rule-based triggers and actions</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Scheduler Status */}
            <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-sm">
              {schedulerStatus.running ? (
                <>
                  <Play size={14} weight="fill" className="text-green-500" />
                  <span className="text-xs font-medium text-gray-700">Scheduler Running</span>
                </>
              ) : (
                <>
                  <Pause size={14} weight="fill" className="text-yellow-500" />
                  <span className="text-xs font-medium text-gray-700">Scheduler Paused</span>
                </>
              )}
            </div>
            
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-sm font-medium text-sm transition-colors"
              data-testid="create-rule-btn"
            >
              <Plus size={18} />
              Create Rule
            </button>
          </div>
        </div>
      </header>

      <div className="p-6">
        {/* Rules List */}
        <div className="bg-white border border-gray-200 rounded-sm">
          <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
            <h2 className="font-bold text-gray-900">Automation Rules</h2>
            <span className="text-xs text-gray-500">{rules.length} rules</span>
          </div>

          {loading ? (
            <div className="flex items-center justify-center p-12">
              <div className="loading-spinner w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full" />
            </div>
          ) : rules.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-12 text-gray-400">
              <Lightning size={48} className="mb-3" />
              <p className="text-sm">No automation rules yet</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 text-green-500 hover:text-green-600 text-sm font-medium"
              >
                Create your first rule
              </button>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {rules.map((rule) => (
                <div key={rule.id} className="p-4" data-testid={`rule-item-${rule.id}`}>
                  {/* Rule Header */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{TRIGGER_ICONS[rule.trigger_type] || '⚡'}</span>
                      <div>
                        <h3 className="font-medium text-gray-900">{rule.name}</h3>
                        <p className="text-xs text-gray-500">
                          Trigger: {rule.trigger_type.replace('_', ' ')} • 
                          Executed: {rule.execution_count} times •
                          Last: {formatDate(rule.last_executed_at)}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {/* Toggle */}
                      <button
                        onClick={() => handleToggle(rule.id)}
                        className={`p-1 rounded transition-colors ${
                          rule.is_active ? 'text-green-500 hover:text-green-600' : 'text-gray-400 hover:text-gray-500'
                        }`}
                        data-testid={`toggle-rule-${rule.id}`}
                      >
                        {rule.is_active ? (
                          <ToggleRight size={28} weight="fill" />
                        ) : (
                          <ToggleLeft size={28} />
                        )}
                      </button>
                      
                      {/* Edit */}
                      <button
                        onClick={() => setEditingRule(rule)}
                        className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                        data-testid={`edit-rule-${rule.id}`}
                      >
                        <PencilSimple size={18} />
                      </button>
                      
                      {/* Delete */}
                      <button
                        onClick={() => handleDelete(rule.id)}
                        className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                        data-testid={`delete-rule-${rule.id}`}
                      >
                        <Trash size={18} />
                      </button>
                      
                      {/* Expand */}
                      <button
                        onClick={() => setExpandedRule(expandedRule === rule.id ? null : rule.id)}
                        className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        {expandedRule === rule.id ? <CaretUp size={18} /> : <CaretDown size={18} />}
                      </button>
                    </div>
                  </div>
                  
                  {/* Expanded Details */}
                  {expandedRule === rule.id && (
                    <div className="mt-4 pl-11 space-y-3">
                      {rule.description && (
                        <p className="text-sm text-gray-600">{rule.description}</p>
                      )}
                      
                      {/* Trigger Config */}
                      {rule.trigger_config && (
                        <div className="text-sm">
                          <span className="font-medium text-gray-700">Trigger Config:</span>
                          <span className="ml-2 text-gray-600">
                            {rule.trigger_config.hours && `After ${rule.trigger_config.hours} hours`}
                            {rule.trigger_config.cron_expression && `Cron: ${rule.trigger_config.cron_expression}`}
                          </span>
                        </div>
                      )}
                      
                      {/* Conditions */}
                      {rule.conditions?.length > 0 && (
                        <div className="text-sm">
                          <span className="font-medium text-gray-700">Conditions:</span>
                          <ul className="ml-2 text-gray-600">
                            {rule.conditions.map((cond, i) => (
                              <li key={i}>
                                {cond.field} {cond.operator} {JSON.stringify(cond.value)}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {/* Actions */}
                      <div className="text-sm">
                        <span className="font-medium text-gray-700">Actions:</span>
                        <ul className="ml-2 space-y-1">
                          {rule.actions.map((action, i) => (
                            <li key={i} className="text-gray-600 flex items-center gap-2">
                              <span className="px-2 py-0.5 bg-gray-100 rounded text-xs font-medium">
                                {ACTION_LABELS[action.action_type] || action.action_type}
                              </span>
                              {action.delay_minutes > 0 && (
                                <span className="text-xs text-gray-400 flex items-center gap-1">
                                  <Clock size={12} /> +{action.delay_minutes}min
                                </span>
                              )}
                              {action.config?.message_text && (
                                <span className="text-xs text-gray-500 truncate max-w-xs">
                                  "{action.config.message_text}"
                                </span>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Scheduler Jobs */}
        <div className="mt-6 bg-white border border-gray-200 rounded-sm">
          <div className="px-4 py-3 border-b border-gray-200">
            <h2 className="font-bold text-gray-900">Scheduled Jobs</h2>
          </div>
          <div className="p-4">
            {schedulerStatus.jobs?.length > 0 ? (
              <div className="space-y-2">
                {schedulerStatus.jobs.map((job) => (
                  <div key={job.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-sm">
                    <div className="flex items-center gap-3">
                      <Clock size={18} className="text-gray-400" />
                      <span className="font-medium text-sm text-gray-700">{job.name}</span>
                    </div>
                    <span className="text-xs text-gray-500">
                      Next run: {job.next_run ? format(new Date(job.next_run), 'MMM d, HH:mm') : 'N/A'}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-400 text-center py-4">No scheduled jobs</p>
            )}
          </div>
        </div>
      </div>

      {/* Create/Edit Modal */}
      {(showCreateModal || editingRule) && (
        <RuleModal
          rule={editingRule}
          triggers={triggers}
          actions={actions}
          agents={agents}
          onClose={() => {
            setShowCreateModal(false);
            setEditingRule(null);
          }}
          onSave={async (data) => {
            if (editingRule) {
              await updateRule(editingRule.id, data);
            } else {
              await createRule(data);
            }
            setShowCreateModal(false);
            setEditingRule(null);
          }}
        />
      )}
    </div>
  );
};

// Rule Create/Edit Modal
const RuleModal = ({ rule, triggers, actions, agents, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: rule?.name || '',
    description: rule?.description || '',
    trigger_type: rule?.trigger_type || 'new_lead',
    trigger_config: rule?.trigger_config || {},
    conditions: rule?.conditions || [],
    actions: rule?.actions || [{ action_type: 'send_message', config: { message_text: '' }, delay_minutes: 0 }],
    is_active: rule?.is_active ?? true,
    priority: rule?.priority || 0
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave(formData);
    } catch (err) {
      console.error('Failed to save rule:', err);
    } finally {
      setSaving(false);
    }
  };

  const updateAction = (index, field, value) => {
    const newActions = [...formData.actions];
    if (field.startsWith('config.')) {
      const configField = field.replace('config.', '');
      newActions[index] = {
        ...newActions[index],
        config: { ...newActions[index].config, [configField]: value }
      };
    } else {
      newActions[index] = { ...newActions[index], [field]: value };
    }
    setFormData({ ...formData, actions: newActions });
  };

  const addAction = () => {
    setFormData({
      ...formData,
      actions: [...formData.actions, { action_type: 'send_message', config: { message_text: '' }, delay_minutes: 0 }]
    });
  };

  const removeAction = (index) => {
    const newActions = formData.actions.filter((_, i) => i !== index);
    setFormData({ ...formData, actions: newActions });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" data-testid="rule-modal">
      <div className="bg-white rounded-sm w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <form onSubmit={handleSubmit}>
          {/* Modal Header */}
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-lg font-bold text-gray-900 font-[Chivo]">
              {rule ? 'Edit Rule' : 'Create Automation Rule'}
            </h2>
            <button type="button" onClick={onClose} className="text-gray-400 hover:text-gray-600">
              ✕
            </button>
          </div>

          {/* Modal Body */}
          <div className="p-4 space-y-4">
            {/* Name & Description */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">
                  Rule Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="w-full p-2 border border-gray-300 rounded-sm text-sm focus:outline-none focus:ring-1 focus:ring-green-500"
                  data-testid="rule-name-input"
                />
              </div>
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">
                  Priority
                </label>
                <input
                  type="number"
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 0 })}
                  className="w-full p-2 border border-gray-300 rounded-sm text-sm focus:outline-none focus:ring-1 focus:ring-green-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={2}
                className="w-full p-2 border border-gray-300 rounded-sm text-sm focus:outline-none focus:ring-1 focus:ring-green-500"
              />
            </div>

            {/* Trigger Type */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">
                Trigger *
              </label>
              <select
                value={formData.trigger_type}
                onChange={(e) => setFormData({ ...formData, trigger_type: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-sm text-sm focus:outline-none focus:ring-1 focus:ring-green-500"
                data-testid="trigger-type-select"
              >
                {triggers.map((t) => (
                  <option key={t.value} value={t.value}>
                    {TRIGGER_ICONS[t.value] || '⚡'} {t.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Trigger Config for no_reply */}
            {formData.trigger_type === 'no_reply' && (
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">
                  Hours without reply
                </label>
                <input
                  type="number"
                  value={formData.trigger_config?.hours || 24}
                  onChange={(e) => setFormData({
                    ...formData,
                    trigger_config: { ...formData.trigger_config, hours: parseInt(e.target.value) || 24 }
                  })}
                  min={1}
                  className="w-full p-2 border border-gray-300 rounded-sm text-sm focus:outline-none focus:ring-1 focus:ring-green-500"
                />
              </div>
            )}

            {/* Actions */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-bold uppercase tracking-wider text-gray-500">
                  Actions *
                </label>
                <button
                  type="button"
                  onClick={addAction}
                  className="text-xs text-green-500 hover:text-green-600 font-medium"
                >
                  + Add Action
                </button>
              </div>
              
              <div className="space-y-3">
                {formData.actions.map((action, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-sm space-y-2">
                    <div className="flex items-center justify-between">
                      <select
                        value={action.action_type}
                        onChange={(e) => updateAction(index, 'action_type', e.target.value)}
                        className="flex-1 p-2 border border-gray-300 rounded-sm text-sm focus:outline-none focus:ring-1 focus:ring-green-500"
                        data-testid={`action-type-select-${index}`}
                      >
                        {actions.map((a) => (
                          <option key={a.value} value={a.value}>{a.label}</option>
                        ))}
                      </select>
                      
                      {formData.actions.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeAction(index)}
                          className="ml-2 p-1 text-red-400 hover:text-red-500"
                        >
                          <Trash size={16} />
                        </button>
                      )}
                    </div>

                    {/* Action Config based on type */}
                    {action.action_type === 'send_message' && (
                      <textarea
                        value={action.config?.message_text || ''}
                        onChange={(e) => updateAction(index, 'config.message_text', e.target.value)}
                        placeholder="Message to send..."
                        rows={2}
                        className="w-full p-2 border border-gray-300 rounded-sm text-sm focus:outline-none focus:ring-1 focus:ring-green-500"
                        data-testid={`action-message-${index}`}
                      />
                    )}

                    {action.action_type === 'assign_lead' && (
                      <div className="grid grid-cols-2 gap-2">
                        <select
                          value={action.config?.assignment_strategy || 'specific'}
                          onChange={(e) => updateAction(index, 'config.assignment_strategy', e.target.value)}
                          className="p-2 border border-gray-300 rounded-sm text-sm"
                        >
                          <option value="specific">Specific Agent</option>
                          <option value="round_robin">Round Robin</option>
                          <option value="least_leads">Least Leads</option>
                        </select>
                        {action.config?.assignment_strategy === 'specific' && (
                          <select
                            value={action.config?.agent_id || ''}
                            onChange={(e) => updateAction(index, 'config.agent_id', e.target.value)}
                            className="p-2 border border-gray-300 rounded-sm text-sm"
                          >
                            <option value="">Select agent...</option>
                            {agents.map((agent) => (
                              <option key={agent.id} value={agent.id}>{agent.name}</option>
                            ))}
                          </select>
                        )}
                      </div>
                    )}

                    {action.action_type === 'update_status' && (
                      <select
                        value={action.config?.new_status || ''}
                        onChange={(e) => updateAction(index, 'config.new_status', e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-sm text-sm"
                      >
                        <option value="">Select status...</option>
                        <option value="new">New</option>
                        <option value="contacted">Contacted</option>
                        <option value="interested">Interested</option>
                        <option value="converted">Converted</option>
                        <option value="lost">Lost</option>
                      </select>
                    )}

                    {action.action_type === 'add_tag' && (
                      <input
                        type="text"
                        value={action.config?.tag || ''}
                        onChange={(e) => updateAction(index, 'config.tag', e.target.value)}
                        placeholder="Tag to add..."
                        className="w-full p-2 border border-gray-300 rounded-sm text-sm"
                      />
                    )}

                    {/* Delay */}
                    <div className="flex items-center gap-2">
                      <Clock size={14} className="text-gray-400" />
                      <input
                        type="number"
                        value={action.delay_minutes}
                        onChange={(e) => updateAction(index, 'delay_minutes', parseInt(e.target.value) || 0)}
                        min={0}
                        className="w-20 p-1 border border-gray-300 rounded-sm text-sm"
                      />
                      <span className="text-xs text-gray-500">minutes delay</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Modal Footer */}
          <div className="p-4 border-t border-gray-200 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving || !formData.name || formData.actions.length === 0}
              className="px-4 py-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white rounded-sm font-medium text-sm transition-colors"
              data-testid="save-rule-btn"
            >
              {saving ? 'Saving...' : rule ? 'Update Rule' : 'Create Rule'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AutomationPage;
