import React, { useEffect, useState, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchHCPs, fetchInteractions, logInteraction, sendChat } from './store/hcpSlice';

function App() {
  const dispatch = useDispatch();
  const { hcps, interactions, tools, loading, error } = useSelector((state) => state.hcp);
  const [chatHistory, setChatHistory] = useState(() => {
    return [];
  });
  const [chatInput, setChatInput] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const chatEndRef = useRef(null);
  const [searchResults, setSearchResults] = useState([]);
  const [interactionSummary, setInteractionSummary] = useState([]);
  const [followups, setFollowups] = useState([]);
  const [formData, setFormData] = useState({
    hcp_name: '',
    hcp_specialty: '',
    interaction_type: '',
    topic: '',
    notes: '',
    outcome: '',
    date: '',
    time: ''
  });

  const scrollToChatBottom = () => {
    setTimeout(() => {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }, 50);
  };

  useEffect(() => {
    dispatch(fetchHCPs());
  }, [dispatch]);

  useEffect(() => {
    scrollToChatBottom();
  }, [chatHistory]);

  const handleFormChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleLogInteraction = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await dispatch(logInteraction(formData)).unwrap();
      dispatch(fetchInteractions());
      alert('Interaction logged successfully!');
      setFormData({
        hcp_name: '',
        hcp_specialty: '',
        interaction_type: '',
        topic: '',
        notes: '',
        outcome: '',
        date: '',
        time: ''
      });
    } catch (err) {
      alert('Error logging interaction: ' + err);
    }
    setSubmitting(false);
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || submitting) return;

    const userMessage = chatInput;
    setChatInput('');
    setSubmitting(true);

    setChatHistory(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const history = chatHistory.map(msg => ({ role: msg.role, content: msg.content }));
      const result = await dispatch(sendChat({ message: userMessage, history })).unwrap();

      setChatHistory(prev => [...prev, { role: 'assistant', content: result.response }]);
      if (result.tool_results) {
        for (const tr of result.tool_results) {
          if (tr.tool === 'log_interaction' && tr.result.success) {
            const data = tr.result;
            const inferSpecialty = (topic) => {
              if (!topic) return 'General';
              const t = topic.toLowerCase();
              if (t.includes('heart') || t.includes('cardio')) return 'Cardiology';
              if (t.includes('cancer') || t.includes('onco')) return 'Oncology';
              if (t.includes('brain') || t.includes('neuro')) return 'Neurology';
              if (t.includes('skin') || t.includes('derma')) return 'Dermatology';
              return 'General';
            };
            
            setFormData({
              hcp_name: data.hcp_name || '',
              hcp_specialty: data.hcp_specialty || inferSpecialty(data.topic),
              interaction_type: data.interaction_type || 'Call',
              topic: data.topic || '',
              notes: data.notes || `Discussion about ${data.topic || 'healthcare'}`,
              outcome: data.outcome || 'Positive',
              date: data.date || '',
              time: data.time || ''
            });
          }
          
          if (tr.tool === 'edit_interaction' && tr.result.success) {
            const fieldName = tr.result.field || tr.result.updated_field;
            const newValue = tr.result.value || tr.result.new_value;
            if (fieldName && newValue) {
              const fieldMap = {
                'hcp_name': 'hcp_name', 'hcp_specialty': 'hcp_specialty',
                'interaction_type': 'interaction_type', 'topic': 'topic',
                'notes': 'notes', 'outcome': 'outcome', 'date': 'date', 'time': 'time'
              };
              setFormData(prev => ({ ...prev, [fieldMap[fieldName] || fieldName]: newValue }));
            }
          }

          if (tr.tool === 'search_hcps' && tr.result.success) {
            setSearchResults(prev => {
              const existing = new Set(prev.map(h => h.id));
              const newItems = (tr.result.hcps || []).filter(h => !existing.has(h.id));
              return [...prev, ...newItems];
            });
          }

          if (tr.tool === 'get_interaction_summary' && tr.result.success) {
            setInteractionSummary(prev => {
              const existing = new Set(prev.map(i => i.id));
              const newItems = (tr.result.interactions || []).filter(i => !existing.has(i.id));
              return [...prev, ...newItems];
            });
          }

          if (tr.tool === 'schedule_followup' && tr.result.success) {
            setFollowups(prev => [...prev, {
              id: tr.result.followup_id,
              hcp_name: tr.result.hcp_name || 'Unknown',
              date: tr.result.date || '',
              time: tr.result.time || '',
              message: tr.result.message || 'Follow-up scheduled'
            }]);
          }
        }
      }
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'assistant', content: 'Error: ' + err }]);
    }
    setSubmitting(false);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <h1>🤖 AI-First HCP CRM</h1>
          <span className="header-subtitle">Healthcare Professional Interaction Manager</span>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <main className="main">
        <div className="content">
          {/* LEFT SIDE - All content scrolls together */}
          <div className="left-panel">
            <div className="section">
              <div className="section-header">
                <h2>📋 Log HCP Interaction</h2>
                <p>Fill details or use AI Assistant to auto-fill</p>
              </div>

              <form onSubmit={handleLogInteraction} className="interaction-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>HCP Name</label>
                    <select name="hcp_name" value={formData.hcp_name} onChange={handleFormChange} required>
                      <option value="">Select HCP</option>
                      {hcps.map(hcp => (
                        <option key={hcp.id} value={hcp.name}>{hcp.name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Specialty</label>
                    <input type="text" name="hcp_specialty" value={formData.hcp_specialty} onChange={handleFormChange} placeholder="e.g. Cardiology" required />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Interaction Type</label>
                    <select name="interaction_type" value={formData.interaction_type} onChange={handleFormChange} required>
                      <option value="">Select Type</option>
                      <option value="Call">Phone Call</option>
                      <option value="Visit">In-Person Visit</option>
                      <option value="Email">Email</option>
                      <option value="Meeting">Virtual Meeting</option>
                      <option value="Product Discussion">Product Discussion</option>
                      <option value="Clinical Trial">Clinical Trial</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Topic</label>
                    <input type="text" name="topic" value={formData.topic} onChange={handleFormChange} placeholder="What was discussed?" required />
                  </div>
                </div>

                <div className="form-group">
                  <label>Notes</label>
                  <textarea name="notes" rows="2" value={formData.notes} onChange={handleFormChange} placeholder="Add notes..." required />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Outcome</label>
                    <select name="outcome" value={formData.outcome} onChange={handleFormChange} required>
                      <option value="">Select Outcome</option>
                      <option value="Positive">Positive</option>
                      <option value="Neutral">Neutral</option>
                      <option value="Negative">Negative</option>
                      <option value="Follow-up Needed">Follow-up Needed</option>
                      <option value="Interested">Interested</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Date & Time</label>
                    <div className="date-time-row">
                      <input type="date" name="date" value={formData.date} onChange={handleFormChange} required />
                      <input type="time" name="time" value={formData.time} onChange={handleFormChange} />
                    </div>
                  </div>
                </div>

                <button type="submit" className="submit-btn" disabled={submitting}>
                  💾 {submitting ? 'Logging...' : 'Log Interaction'}
                </button>
              </form>

              <div className="left-section-divider"></div>

              <h3 className="left-section-title">📊 Recent Interactions</h3>
              <div className="interactions-list">
                {interactions.length === 0 ? (
                  <p className="empty-text">No interactions logged yet</p>
                ) : (
                  interactions.map(interaction => (
                    <div key={interaction.id} className="interaction-item">
                      <div className="interaction-info">
                        <span className="hcp-name">{interaction.hcp_name}</span>
                        <span className="interaction-detail">{interaction.interaction_type} • {interaction.topic}</span>
                      </div>
                      <span className={`outcome-badge ${interaction.outcome?.toLowerCase()}`}>{interaction.outcome}</span>
                    </div>
                  ))
                )}
              </div>

              <div className="left-section-divider"></div>

              <h3 className="left-section-title">🔍 Search Results</h3>
              {searchResults.length === 0 ? (
                <p className="empty-text">No search results yet</p>
              ) : (
                searchResults.map((hcp, idx) => (
                  <div key={idx} className="result-item">
                    <strong>{hcp.name}</strong>
                    <span>{hcp.specialty} - {hcp.hospital}</span>
                  </div>
                ))
              )}

              <div className="left-section-divider"></div>

              <h3 className="left-section-title">📊 Interaction Summary</h3>
              {interactionSummary.length === 0 ? (
                <p className="empty-text">No interactions found</p>
              ) : (
                interactionSummary.map((item, idx) => (
                  <div key={idx} className="result-item">
                    <strong>{item.hcp_name}</strong>
                    <span>{item.interaction_type} - {item.topic}</span>
                  </div>
                ))
              )}

              <div className="left-section-divider"></div>

              <h3 className="left-section-title">📅 Scheduled Follow-ups</h3>
              {followups.length === 0 ? (
                <p className="empty-text">No follow-ups scheduled</p>
              ) : (
                followups.map((fu, idx) => (
                  <div key={idx} className="result-item followup-item">
                    <strong>{fu.hcp_name}</strong>
                    <span>{fu.date} - {fu.time || ''}</span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* RIGHT SIDE - AI Assistant */}
          <div className="right-panel">
            <section className="section chat-section">
              <div className="section-header">
                <h2>💬 AI Assistant</h2>
                <p>Chat to auto-fill form or manage interactions</p>
              </div>

              <div className="chat-messages">
                {chatHistory.length === 0 ? (
                  <div className="chat-empty">
                    <div className="chat-icon">🤖</div>
                    <p>Hello! I'm your AI Assistant</p>
                    <p className="chat-hint">Try: "Log a call with Dr. Sarah about cardiology on 22/05/2026 at 11am"</p>
                  </div>
                ) : (
                  chatHistory.map((msg, idx) => (
                    <div key={idx} className={`chat-message ${msg.role}`}>
                      <div className="message-avatar">{msg.role === 'user' ? '👤' : '🤖'}</div>
                      <div className="message-bubble">
                        <div className="message-label">{msg.role === 'user' ? 'You' : 'AI'}</div>
                        <div className="message-text">{msg.content}</div>
                      </div>
                    </div>
                  ))
                )}
                {submitting && (
                  <div className="chat-message assistant">
                    <div className="message-avatar">🤖</div>
                    <div className="message-bubble">
                      <div className="message-label">AI</div>
                      <div className="message-text loading">Processing...</div>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              <form onSubmit={handleChatSubmit} className="chat-form">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Type your message..."
                  className="chat-input"
                  disabled={submitting}
                />
                <button type="submit" className="send-btn" disabled={submitting || !chatInput.trim()}>
                  ➤
                </button>
              </form>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;