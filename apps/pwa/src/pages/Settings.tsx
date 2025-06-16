import React, { useState } from 'react'
import { Save, Bell, Shield, Database, Zap, ExternalLink, Key, Mail, MessageSquare } from 'lucide-react'

export function Settings() {
  const [activeTab, setActiveTab] = useState('general')
  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      push: true,
      sms: false,
      webhook: true,
    },
    analytics: {
      retentionPeriod: 90,
      enableRealTime: true,
      exportFormat: 'json',
    },
    security: {
      sessionTimeout: 60,
      mfaEnabled: false,
      ipWhitelist: [],
    },
    integrations: {
      crm: {
        enabled: false,
        provider: '',
        apiKey: '',
      },
      email: {
        enabled: true,
        provider: 'sendgrid',
        apiKey: '••••••••••••',
      },
      sms: {
        enabled: false,
        provider: '',
        apiKey: '',
      },
    },
  })

  const tabs = [
    { id: 'general', name: 'General', icon: Settings },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'analytics', name: 'Analytics', icon: Database },
    { id: 'integrations', name: 'Integrations', icon: Zap },
  ]

  const handleSave = () => {
    // Save settings logic would go here
    console.log('Saving settings:', settings)
  }

  const updateSetting = (section: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section as keyof typeof prev],
        [key]: value,
      },
    }))
  }

  const updateNestedSetting = (section: string, subsection: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section as keyof typeof prev],
        [subsection]: {
          ...(prev[section as keyof typeof prev] as any)[subsection],
          [key]: value,
        },
      },
    }))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-1">
            Configure your NGX Voice Agent platform
          </p>
        </div>
        <button onClick={handleSave} className="btn-primary">
          <Save className="w-4 h-4 mr-2" />
          Save Changes
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  activeTab === tab.id
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <tab.icon className="w-5 h-5 mr-3" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <div className="card">
            {activeTab === 'general' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    General Settings
                  </h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="label">Organization Name</label>
                    <input
                      type="text"
                      defaultValue="NGX Voice Agent"
                      className="input mt-1"
                    />
                  </div>
                  <div>
                    <label className="label">Time Zone</label>
                    <select className="input mt-1">
                      <option>UTC-8 (Pacific Time)</option>
                      <option>UTC-5 (Eastern Time)</option>
                      <option>UTC+0 (GMT)</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="label">Default Language</label>
                  <select className="input mt-1 max-w-xs">
                    <option>English (US)</option>
                    <option>Spanish (ES)</option>
                    <option>French (FR)</option>
                  </select>
                </div>

                <div>
                  <label className="label">Brand Colors</label>
                  <div className="grid grid-cols-3 gap-4 mt-2">
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">Primary</label>
                      <input type="color" defaultValue="#3b82f6" className="w-full h-10 rounded border" />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">Secondary</label>
                      <input type="color" defaultValue="#1f2937" className="w-full h-10 rounded border" />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">Accent</label>
                      <input type="color" defaultValue="#10b981" className="w-full h-10 rounded border" />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    Notification Preferences
                  </h2>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Mail className="w-5 h-5 text-gray-500" />
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">Email Notifications</h3>
                        <p className="text-sm text-gray-500">Receive alerts via email</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifications.email}
                        onChange={(e) => updateSetting('notifications', 'email', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Bell className="w-5 h-5 text-gray-500" />
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">Push Notifications</h3>
                        <p className="text-sm text-gray-500">Browser push notifications</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifications.push}
                        onChange={(e) => updateSetting('notifications', 'push', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <MessageSquare className="w-5 h-5 text-gray-500" />
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">SMS Notifications</h3>
                        <p className="text-sm text-gray-500">Critical alerts via SMS</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifications.sms}
                        onChange={(e) => updateSetting('notifications', 'sms', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <ExternalLink className="w-5 h-5 text-gray-500" />
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">Webhook Notifications</h3>
                        <p className="text-sm text-gray-500">Send data to external systems</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifications.webhook}
                        onChange={(e) => updateSetting('notifications', 'webhook', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    Security Settings
                  </h2>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="label">Session Timeout (minutes)</label>
                    <input
                      type="number"
                      value={settings.security.sessionTimeout}
                      onChange={(e) => updateSetting('security', 'sessionTimeout', parseInt(e.target.value))}
                      className="input mt-1 max-w-xs"
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">Two-Factor Authentication</h3>
                      <p className="text-sm text-gray-500">Add an extra layer of security to your account</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.security.mfaEnabled}
                        onChange={(e) => updateSetting('security', 'mfaEnabled', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>

                  <div>
                    <label className="label">API Keys</label>
                    <div className="space-y-3 mt-2">
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <span className="text-sm font-medium">Production API Key</span>
                          <p className="text-xs text-gray-500">••••••••••••••••••••••••••••••••</p>
                        </div>
                        <button className="btn-secondary text-xs">Regenerate</button>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <span className="text-sm font-medium">Development API Key</span>
                          <p className="text-xs text-gray-500">••••••••••••••••••••••••••••••••</p>
                        </div>
                        <button className="btn-secondary text-xs">Regenerate</button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'analytics' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    Analytics & Data
                  </h2>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="label">Data Retention Period (days)</label>
                    <select 
                      value={settings.analytics.retentionPeriod}
                      onChange={(e) => updateSetting('analytics', 'retentionPeriod', parseInt(e.target.value))}
                      className="input mt-1 max-w-xs"
                    >
                      <option value={30}>30 days</option>
                      <option value={90}>90 days</option>
                      <option value={365}>1 year</option>
                      <option value={-1}>Forever</option>
                    </select>
                  </div>

                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">Real-time Analytics</h3>
                      <p className="text-sm text-gray-500">Enable live data updates in dashboard</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.analytics.enableRealTime}
                        onChange={(e) => updateSetting('analytics', 'enableRealTime', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>

                  <div>
                    <label className="label">Export Format</label>
                    <select 
                      value={settings.analytics.exportFormat}
                      onChange={(e) => updateSetting('analytics', 'exportFormat', e.target.value)}
                      className="input mt-1 max-w-xs"
                    >
                      <option value="json">JSON</option>
                      <option value="csv">CSV</option>
                      <option value="xlsx">Excel</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'integrations' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    Integrations
                  </h2>
                </div>

                <div className="space-y-6">
                  {/* CRM Integration */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">CRM Integration</h3>
                        <p className="text-sm text-gray-500">Connect to your CRM system</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.integrations.crm.enabled}
                          onChange={(e) => updateNestedSetting('integrations', 'crm', 'enabled', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                      </label>
                    </div>
                    {settings.integrations.crm.enabled && (
                      <div className="space-y-3">
                        <div>
                          <label className="label text-xs">Provider</label>
                          <select className="input mt-1">
                            <option>Salesforce</option>
                            <option>HubSpot</option>
                            <option>Pipedrive</option>
                          </select>
                        </div>
                        <div>
                          <label className="label text-xs">API Key</label>
                          <input type="password" placeholder="Enter API key" className="input mt-1" />
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Email Integration */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">Email Service</h3>
                        <p className="text-sm text-gray-500">Configure email notifications</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.integrations.email.enabled}
                          onChange={(e) => updateNestedSetting('integrations', 'email', 'enabled', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                      </label>
                    </div>
                    {settings.integrations.email.enabled && (
                      <div className="space-y-3">
                        <div>
                          <label className="label text-xs">Provider</label>
                          <select 
                            value={settings.integrations.email.provider}
                            onChange={(e) => updateNestedSetting('integrations', 'email', 'provider', e.target.value)}
                            className="input mt-1"
                          >
                            <option value="sendgrid">SendGrid</option>
                            <option value="mailgun">Mailgun</option>
                            <option value="ses">Amazon SES</option>
                          </select>
                        </div>
                        <div>
                          <label className="label text-xs">API Key</label>
                          <input 
                            type="password" 
                            value={settings.integrations.email.apiKey}
                            onChange={(e) => updateNestedSetting('integrations', 'email', 'apiKey', e.target.value)}
                            className="input mt-1" 
                          />
                        </div>
                      </div>
                    )}
                  </div>

                  {/* SMS Integration */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">SMS Service</h3>
                        <p className="text-sm text-gray-500">Send SMS notifications</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.integrations.sms.enabled}
                          onChange={(e) => updateNestedSetting('integrations', 'sms', 'enabled', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                      </label>
                    </div>
                    {settings.integrations.sms.enabled && (
                      <div className="space-y-3">
                        <div>
                          <label className="label text-xs">Provider</label>
                          <select className="input mt-1">
                            <option>Twilio</option>
                            <option>MessageBird</option>
                            <option>Vonage</option>
                          </select>
                        </div>
                        <div>
                          <label className="label text-xs">API Key</label>
                          <input type="password" placeholder="Enter API key" className="input mt-1" />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}