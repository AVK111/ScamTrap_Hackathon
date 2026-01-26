import { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [scamMessage, setScamMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [isActive, setIsActive] = useState(false);
  const [persona, setPersona] = useState(null);
  const [intelligence, setIntelligence] = useState({
    scamType: 'Unknown',
    extractedData: [],
    timeWasted: 0,
    attempts: 0
  });
  const [leaderboard, setLeaderboard] = useState([
    { rank: 1, name: 'PhishKing2024', type: 'Bank Fraud', timeWasted: 3847, attempts: 23 },
    { rank: 2, name: 'LotteryScam_Pro', type: 'Lottery', timeWasted: 2901, attempts: 18 },
    { rank: 3, name: 'JobOffer_Fake', type: 'Job Scam', timeWasted: 2456, attempts: 15 },
    { rank: 4, name: 'CryptoHunter99', type: 'Crypto', timeWasted: 1823, attempts: 12 },
    { rank: 5, name: 'UPI_Collector', type: 'Payment', timeWasted: 1234, attempts: 9 }
  ]);
  const [currentView, setCurrentView] = useState('main'); // 'main' or 'leaderboard'
  
  const messagesEndRef = useRef(null);
  const timerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Sample personas for different scam types
  const personas = {
    bank: {
      name: 'Ramesh Kumar',
      age: 58,
      job: 'Retired Teacher',
      city: 'Pune',
      bank: 'State Bank of India',
      techLevel: 'Low',
      avatar: '👴'
    },
    job: {
      name: 'Priya Sharma',
      age: 23,
      job: 'Fresh Graduate',
      city: 'Delhi',
      bank: 'HDFC Bank',
      techLevel: 'Medium',
      avatar: '👩‍🎓'
    },
    lottery: {
      name: 'Suresh Patel',
      age: 45,
      job: 'Shop Owner',
      city: 'Ahmedabad',
      bank: 'ICICI Bank',
      techLevel: 'Low',
      avatar: '👨‍💼'
    },
    crypto: {
      name: 'Vikram Malhotra',
      age: 32,
      job: 'Software Engineer',
      city: 'Bangalore',
      bank: 'Axis Bank',
      techLevel: 'High',
      avatar: '👨‍💻'
    }
  };

  // Sample conversation flows
  const conversationFlows = {
    bank: [
      { sender: 'scammer', text: 'Dear customer, your bank account has been blocked. Please verify your details immediately.' },
      { sender: 'ai', text: 'Oh no! What happened? I am not understanding...' },
      { sender: 'scammer', text: 'You need to provide your ATM card number and CVV to unlock.' },
      { sender: 'ai', text: 'CVV means? Where I can find? My son usually helps me with these things...' },
      { sender: 'scammer', text: 'It\'s on the back of your card. 3 digits. Please share quickly!' },
      { sender: 'ai', text: 'Wait wait... let me find my card. One minute... my eyes are not good...' },
      { sender: 'scammer', text: 'Please hurry! Your account will be permanently blocked!' },
      { sender: 'ai', text: 'Okay okay... I am trying... but which numbers you want? There are so many numbers on card...' }
    ],
    job: [
      { sender: 'scammer', text: 'Congratulations! You have been selected for Google Software Engineer position. Salary 15 LPA.' },
      { sender: 'ai', text: 'OMG really?? I applied to so many places! This is amazing! 😍' },
      { sender: 'scammer', text: 'Yes, but you need to pay Rs. 5000 for documentation and verification.' },
      { sender: 'ai', text: 'Oh... I need to pay? But I thought companies hire for free?' },
      { sender: 'scammer', text: 'This is just a refundable security deposit. All big companies do this.' },
      { sender: 'ai', text: 'Hmm okay... but I need to ask my parents first. Can I pay tomorrow?' },
      { sender: 'scammer', text: 'No! The position will go to someone else. Pay now via UPI.' },
      { sender: 'ai', text: 'But I only have Rs. 2000 in my account right now... can you take that first?' }
    ],
    lottery: [
      { sender: 'scammer', text: 'Congratulations! You won Rs. 25 LAKHS in KBC lottery!' },
      { sender: 'ai', text: 'What?! Really?! I never won anything in my life! 🎉' },
      { sender: 'scammer', text: 'Yes sir! But you need to pay Rs. 10,000 tax first to claim the prize.' },
      { sender: 'ai', text: 'Tax? Okay okay... but Rs. 10,000 is big amount for me... can I pay Rs. 5000 first?' },
      { sender: 'scammer', text: 'No sir, full amount is required. You will get 25 lakhs back!' },
      { sender: 'ai', text: 'Let me ask my wife... she handles all money matters... one minute...' },
      { sender: 'scammer', text: 'Sir please don\'t tell anyone! This is confidential prize!' },
      { sender: 'ai', text: 'Oh okay okay... but how I will receive 25 lakhs? In my bank account?' }
    ],
    crypto: [
      { sender: 'scammer', text: 'Exclusive crypto investment opportunity! 300% returns guaranteed in 30 days.' },
      { sender: 'ai', text: 'Interesting! Which blockchain is this on? Ethereum or BSC?' },
      { sender: 'scammer', text: 'It\'s our proprietary blockchain. Much faster and secure.' },
      { sender: 'ai', text: 'Proprietary? Is the smart contract audited? Can I see the GitHub repo?' },
      { sender: 'scammer', text: 'It\'s closed source for security. Just invest minimum Rs. 50,000 to start.' },
      { sender: 'ai', text: 'Hmm... but 300% in 30 days is like... 10% daily? That\'s suspicious tbh...' },
      { sender: 'scammer', text: 'Not suspicious! Our AI trading bot makes this possible!' },
      { sender: 'ai', text: 'AI trading? What\'s the Sharpe ratio? And what about slippage on large orders?' }
    ]
  };

  const detectScamType = (message) => {
    const lower = message.toLowerCase();
    if (lower.includes('bank') || lower.includes('account') || lower.includes('atm') || lower.includes('card')) {
      return 'bank';
    }
    if (lower.includes('job') || lower.includes('selected') || lower.includes('interview') || lower.includes('salary')) {
      return 'job';
    }
    if (lower.includes('lottery') || lower.includes('won') || lower.includes('prize') || lower.includes('kbc')) {
      return 'lottery';
    }
    if (lower.includes('crypto') || lower.includes('bitcoin') || lower.includes('investment') || lower.includes('trading')) {
      return 'crypto';
    }
    return 'bank'; // default
  };

  const extractIntelligence = (text) => {
    const extracted = [];
    
    // UPI ID regex
    const upiRegex = /[\w.-]+@[\w.-]+/g;
    const upiMatches = text.match(upiRegex);
    if (upiMatches) {
      upiMatches.forEach(upi => {
        if (!intelligence.extractedData.includes(`UPI: ${upi}`)) {
          extracted.push(`UPI: ${upi}`);
        }
      });
    }

    // Phone number regex
    const phoneRegex = /(\+91|91)?[\s-]?[6-9]\d{9}/g;
    const phoneMatches = text.match(phoneRegex);
    if (phoneMatches) {
      phoneMatches.forEach(phone => {
        if (!intelligence.extractedData.includes(`Phone: ${phone}`)) {
          extracted.push(`Phone: ${phone}`);
        }
      });
    }

    // URL regex
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const urlMatches = text.match(urlRegex);
    if (urlMatches) {
      urlMatches.forEach(url => {
        if (!intelligence.extractedData.includes(`URL: ${url}`)) {
          extracted.push(`URL: ${url}`);
        }
      });
    }

    return extracted;
  };

  const handleHandOver = () => {
    if (!scamMessage.trim()) return;

    const scamType = detectScamType(scamMessage);
    const selectedPersona = personas[scamType];
    const conversationFlow = conversationFlows[scamType];

    setPersona(selectedPersona);
    setIsActive(true);
    setMessages([{ sender: 'scammer', text: scamMessage, timestamp: new Date() }]);
    setIntelligence({
      scamType: scamType.charAt(0).toUpperCase() + scamType.slice(1),
      extractedData: [],
      timeWasted: 0,
      attempts: 0
    });

    // Start timer
    timerRef.current = setInterval(() => {
      setIntelligence(prev => ({
        ...prev,
        timeWasted: prev.timeWasted + 1
      }));
    }, 1000);

    // Simulate conversation flow
    let index = 1;
    const interval = setInterval(() => {
      if (index >= conversationFlow.length) {
        clearInterval(interval);
        return;
      }

      const msg = conversationFlow[index];
      setMessages(prev => [...prev, { ...msg, timestamp: new Date() }]);

      // Extract intelligence from scammer messages
      if (msg.sender === 'scammer') {
        const extracted = extractIntelligence(msg.text);
        if (extracted.length > 0) {
          setIntelligence(prev => ({
            ...prev,
            extractedData: [...prev.extractedData, ...extracted],
            attempts: prev.attempts + 1
          }));
        }
      }

      index++;
    }, 3000);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      
      {/* Header */}
      <header className="bg-black/50 backdrop-blur-lg border-b border-gray-700 px-6 py-4 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="text-3xl">🕵️</div>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-red-500 via-orange-500 to-yellow-500 bg-clip-text text-transparent">
              ScamTrap AI
            </h1>
            <p className="text-xs text-gray-400">Autonomous Multi-Agent Deception System</p>
          </div>
        </div>
        
        <div className="flex gap-4">
          <button 
            onClick={() => setCurrentView('main')}
            className={`px-4 py-2 rounded-lg font-semibold transition-all ${
              currentView === 'main' 
                ? 'bg-red-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            🎯 Active Trap
          </button>
          <button 
            onClick={() => setCurrentView('leaderboard')}
            className={`px-4 py-2 rounded-lg font-semibold transition-all ${
              currentView === 'leaderboard' 
                ? 'bg-red-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            🏆 Leaderboard
          </button>
        </div>

        <div className="flex items-center gap-2 px-4 py-2 bg-green-500/20 border border-green-500 rounded-lg">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-green-400 font-semibold text-sm">Ethical Mode: ON</span>
        </div>
      </header>

      {/* Main View */}
      {currentView === 'main' ? (
        <div className="flex flex-1 p-6 gap-6 max-w-[1800px] mx-auto">
          
          {/* Left Side - Chat Area */}
          <div className="flex-1 flex flex-col gap-4">
            
            {/* Initial Input */}
            {!isActive && (
              <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700 shadow-2xl">
                <h2 className="text-xl font-bold mb-2 flex items-center gap-2">
                  <span>🎣</span> Deploy the Trap
                </h2>
                <p className="text-gray-400 text-sm mb-4">Paste a scam message to activate the autonomous agent system</p>
                
                <textarea
                  value={scamMessage}
                  onChange={(e) => setScamMessage(e.target.value)}
                  className="w-full h-32 bg-gray-900 border-2 border-gray-600 rounded-lg px-4 py-3 resize-none focus:outline-none focus:border-red-500 transition-all text-white placeholder-gray-500"
                  placeholder="Example: 'Congratulations! You won Rs. 25 LAKHS in KBC lottery! Call now to claim...'"
                />
                
                <button 
                  onClick={handleHandOver}
                  className="mt-4 w-full bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white px-6 py-3 rounded-lg font-bold text-lg transition-all transform hover:scale-105 shadow-lg"
                >
                  🤖 Hand Over to AI Agents
                </button>
              </div>
            )}

            {/* Active Conversation */}
            {isActive && (
              <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700 shadow-2xl flex flex-col h-[calc(100vh-200px)]">
                <div className="flex justify-between items-center mb-4 pb-4 border-b border-gray-700">
                  <h2 className="text-xl font-bold flex items-center gap-2">
                    <span className="animate-pulse">🔴</span> Live Engagement
                  </h2>
                  <div className="text-sm text-gray-400">
                    Time Wasted: <span className="text-red-400 font-bold">{formatTime(intelligence.timeWasted)}</span>
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                  {messages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex ${msg.sender === 'ai' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
                    >
                      <div
                        className={`max-w-[70%] px-4 py-3 rounded-2xl ${
                          msg.sender === 'ai'
                            ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white'
                            : 'bg-gray-700 text-gray-100'
                        }`}
                      >
                        <div className="text-xs opacity-75 mb-1">
                          {msg.sender === 'ai' ? `🤖 ${persona?.name}` : '👤 Scammer'}
                        </div>
                        <div>{msg.text}</div>
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>

                {/* Typing indicator */}
                <div className="flex items-center gap-2 text-gray-400 text-sm">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                  <span>AI is typing...</span>
                </div>
              </div>
            )}
          </div>

          {/* Right Side - Intelligence Panel */}
          <div className="w-96 flex flex-col gap-4">
            
            {/* Persona Card */}
            {persona && (
              <div className="bg-gradient-to-br from-purple-900/50 to-blue-900/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/30 shadow-2xl">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span>🎭</span> Active Persona
                </h3>
                <div className="flex items-center gap-4 mb-4">
                  <div className="text-5xl">{persona.avatar}</div>
                  <div>
                    <div className="font-bold text-xl">{persona.name}</div>
                    <div className="text-sm text-gray-300">{persona.age} yrs • {persona.city}</div>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Occupation:</span>
                    <span className="font-semibold">{persona.job}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Bank:</span>
                    <span className="font-semibold">{persona.bank}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Tech Literacy:</span>
                    <span className={`font-semibold ${
                      persona.techLevel === 'Low' ? 'text-red-400' : 
                      persona.techLevel === 'Medium' ? 'text-yellow-400' : 'text-green-400'
                    }`}>
                      {persona.techLevel}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Intelligence Panel */}
            <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700 shadow-2xl flex-1">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <span>🧠</span> Live Intelligence
              </h3>
              
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-gray-400 mb-1">Scam Classification</div>
                  <div className="px-3 py-2 bg-red-500/20 border border-red-500 rounded-lg font-semibold text-red-400">
                    {intelligence.scamType}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-gray-400 mb-2">Extracted Data</div>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {intelligence.extractedData.length === 0 ? (
                      <div className="text-gray-500 text-sm italic">No data extracted yet...</div>
                    ) : (
                      intelligence.extractedData.map((data, idx) => (
                        <div key={idx} className="px-3 py-2 bg-yellow-500/20 border border-yellow-500 rounded-lg text-yellow-400 text-sm font-mono">
                          {data}
                        </div>
                      ))
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-400 mb-1">Time Wasted</div>
                    <div className="text-2xl font-bold text-red-400">{formatTime(intelligence.timeWasted)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400 mb-1">Extraction Attempts</div>
                    <div className="text-2xl font-bold text-orange-400">{intelligence.attempts}</div>
                  </div>
                </div>
              </div>

              {/* Safety Indicators */}
              <div className="mt-6 pt-4 border-t border-gray-700 space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-green-400">No Real Data Shared</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-green-400">OTP Blocks Active</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-green-400">Law Enforcement Ready</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Leaderboard View */
        <div className="p-6 max-w-[1400px] mx-auto">
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-8 border border-gray-700 shadow-2xl">
            <h2 className="text-3xl font-bold mb-2 flex items-center gap-3">
              <span>🏆</span> Scammer Leaderboard
            </h2>
            <p className="text-gray-400 mb-6">Top scam operations ranked by time wasted</p>

            <div className="space-y-3">
              {leaderboard.map((entry) => (
                <div
                  key={entry.rank}
                  className={`flex items-center justify-between p-4 rounded-xl border transition-all hover:scale-[1.02] ${
                    entry.rank === 1
                      ? 'bg-gradient-to-r from-yellow-600/20 to-yellow-700/20 border-yellow-500'
                      : entry.rank === 2
                      ? 'bg-gradient-to-r from-gray-400/20 to-gray-500/20 border-gray-400'
                      : entry.rank === 3
                      ? 'bg-gradient-to-r from-orange-600/20 to-orange-700/20 border-orange-500'
                      : 'bg-gray-700/50 border-gray-600'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div className={`text-3xl font-bold ${
                      entry.rank === 1 ? 'text-yellow-400' :
                      entry.rank === 2 ? 'text-gray-400' :
                      entry.rank === 3 ? 'text-orange-400' :
                      'text-gray-500'
                    }`}>
                      #{entry.rank}
                    </div>
                    <div>
                      <div className="font-bold text-lg">{entry.name}</div>
                      <div className="text-sm text-gray-400">{entry.type}</div>
                    </div>
                  </div>

                  <div className="flex gap-8 items-center">
                    <div className="text-center">
                      <div className="text-sm text-gray-400">Time Wasted</div>
                      <div className="text-xl font-bold text-red-400">{formatTime(entry.timeWasted)}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-400">Attempts</div>
                      <div className="text-xl font-bold text-orange-400">{entry.attempts}</div>
                    </div>
                    <div className="text-3xl">
                      {entry.rank === 1 ? '🥇' : entry.rank === 2 ? '🥈' : entry.rank === 3 ? '🥉' : '🎯'}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Stats Summary */}
            <div className="mt-8 grid grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-red-900/30 to-red-800/30 p-4 rounded-xl border border-red-700">
                <div className="text-sm text-gray-400 mb-1">Total Time Wasted</div>
                <div className="text-2xl font-bold text-red-400">
                  {formatTime(leaderboard.reduce((sum, entry) => sum + entry.timeWasted, 0))}
                </div>
              </div>
              <div className="bg-gradient-to-br from-orange-900/30 to-orange-800/30 p-4 rounded-xl border border-orange-700">
                <div className="text-sm text-gray-400 mb-1">Total Attempts Blocked</div>
                <div className="text-2xl font-bold text-orange-400">
                  {leaderboard.reduce((sum, entry) => sum + entry.attempts, 0)}
                </div>
              </div>
              <div className="bg-gradient-to-br from-green-900/30 to-green-800/30 p-4 rounded-xl border border-green-700">
                <div className="text-sm text-gray-400 mb-1">Active Traps</div>
                <div className="text-2xl font-bold text-green-400">{leaderboard.length}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
