/**
 * AI Chat Context
 * 
 * Manages AI conversation state, messages, and interactions
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import { message } from 'antd';
import { apiService } from '../services/api';

const AIChatContext = createContext();

export const useAIChat = () => {
  const context = useContext(AIChatContext);
  if (!context) {
    throw new Error('useAIChat must be used within an AIChatProvider');
  }
  return context;
};

export const AIChatProvider = ({ children }) => {
  const [conversations, setConversations] = useState(new Map());
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Get current conversation
  const currentConversation = conversations.get(currentConversationId) || {
    id: null,
    messages: [],
    context: {},
    status: 'active'
  };

  // Create new conversation
  const startNewConversation = useCallback(() => {
    const conversationId = 'chat-' + Date.now();
    const newConversation = {
      id: conversationId,
      messages: [
        {
          id: 'welcome-' + Date.now(),
          type: 'ai',
          content: {
            text: "🌟 Hi there! I'm your AI travel assistant. I can help you plan amazing trips, analyze travel photos, and answer any questions about destinations worldwide!\n\nHow can I help you today? You can:\n• Ask about destinations\n• Plan a trip\n• Upload a photo for inspiration\n• Use voice commands",
          },
          timestamp: new Date().toISOString(),
          suggested_actions: [
            'Plan a trip to Paris',
            'Show me beach destinations',
            'I want an adventure trip',
            'Budget travel ideas'
          ]
        }
      ],
      context: {
        user_preferences: {},
        current_trip: null,
        conversation_stage: 'greeting'
      },
      status: 'active',
      createdAt: new Date().toISOString()
    };

    setConversations(prev => new Map(prev).set(conversationId, newConversation));
    setCurrentConversationId(conversationId);
    return conversationId;
  }, []);

  // Send text message
  const sendMessage = useCallback(async (text, options = {}) => {
    if (!text.trim()) return;

    const conversationId = currentConversationId || startNewConversation();
    const messageId = 'msg-' + Date.now();

    // Add user message
    const userMessage = {
      id: messageId,
      type: 'user',
      content: { text: text.trim() },
      timestamp: new Date().toISOString()
    };

    // Update conversation with user message
    setConversations(prev => {
      const updated = new Map(prev);
      const conversation = updated.get(conversationId);
      if (conversation) {
        conversation.messages = [...conversation.messages, userMessage];
        updated.set(conversationId, conversation);
      }
      return updated;
    });

    // Show typing indicator
    setIsTyping(true);

    try {
      // Try to call AI API
      const response = await apiService.ai.startConversation({
        message: text,
        conversation_id: conversationId,
        context: currentConversation.context
      });

      const aiMessage = {
        id: 'ai-' + Date.now(),
        type: 'ai',
        content: {
          text: response.data.response,
          suggested_actions: response.data.suggested_actions || []
        },
        timestamp: new Date().toISOString(),
        context: response.data.context
      };

      // Update conversation with AI response
      setConversations(prev => {
        const updated = new Map(prev);
        const conversation = updated.get(conversationId);
        if (conversation) {
          conversation.messages = [...conversation.messages, aiMessage];
          conversation.context = { ...conversation.context, ...response.data.context };
          updated.set(conversationId, conversation);
        }
        return updated;
      });

    } catch (error) {
      console.warn('AI API call failed, using mock response:', error);
      
      // Generate mock AI response
      const mockResponse = generateMockAIResponse(text, currentConversation.context);
      
      const aiMessage = {
        id: 'ai-' + Date.now(),
        type: 'ai',
        content: {
          text: mockResponse.text,
          suggested_actions: mockResponse.suggested_actions || []
        },
        timestamp: new Date().toISOString()
      };

      // Update conversation with mock response
      setConversations(prev => {
        const updated = new Map(prev);
        const conversation = updated.get(conversationId);
        if (conversation) {
          conversation.messages = [...conversation.messages, aiMessage];
          updated.set(conversationId, conversation);
        }
        return updated;
      });
    } finally {
      setIsTyping(false);
    }
  }, [currentConversationId, currentConversation, startNewConversation]);

  // Send voice message
  const sendVoiceMessage = useCallback(async (audioBlob) => {
    setIsRecording(true);
    setIsTyping(true);

    try {
      // Try to call voice API
      const response = await apiService.ai.processVoice(audioBlob);
      
      if (response.data.transcription) {
        await sendMessage(response.data.transcription);
      }
    } catch (error) {
      console.warn('Voice API call failed:', error);
      message.error('Voice processing is not available yet. Please type your message.');
    } finally {
      setIsRecording(false);
      setIsTyping(false);
    }
  }, [sendMessage]);

  // Analyze image
  const analyzeImage = useCallback(async (imageFile, prompt = "What destination does this suggest?") => {
    setIsAnalyzing(true);
    const conversationId = currentConversationId || startNewConversation();

    // Add user image message
    const imageMessage = {
      id: 'img-' + Date.now(),
      type: 'user',
      content: {
        image: {
          file: imageFile,
          url: URL.createObjectURL(imageFile),
          prompt: prompt
        }
      },
      timestamp: new Date().toISOString()
    };

    setConversations(prev => {
      const updated = new Map(prev);
      const conversation = updated.get(conversationId);
      if (conversation) {
        conversation.messages = [...conversation.messages, imageMessage];
        updated.set(conversationId, conversation);
      }
      return updated;
    });

    try {
      // Try to call image analysis API
      const response = await apiService.ai.analyzeImage(imageFile, prompt);
      
      const aiMessage = {
        id: 'ai-img-' + Date.now(),
        type: 'ai',
        content: {
          text: response.data.suggestions || 'Image analysis completed!',
          image_analysis: response.data.vision_analysis
        },
        timestamp: new Date().toISOString()
      };

      setConversations(prev => {
        const updated = new Map(prev);
        const conversation = updated.get(conversationId);
        if (conversation) {
          conversation.messages = [...conversation.messages, aiMessage];
          updated.set(conversationId, conversation);
        }
        return updated;
      });

    } catch (error) {
      console.warn('Image analysis API failed, using mock response:', error);
      
      const mockResponse = {
        text: `🖼️ I can see this is a beautiful image! While my image analysis is still being set up, I can help you plan trips based on your description. What type of destination or experience are you looking for?`,
        suggested_actions: [
          'Plan a scenic trip',
          'Beach destinations', 
          'Mountain adventures',
          'City experiences'
        ]
      };

      const aiMessage = {
        id: 'ai-img-' + Date.now(),
        type: 'ai',
        content: mockResponse,
        timestamp: new Date().toISOString()
      };

      setConversations(prev => {
        const updated = new Map(prev);
        const conversation = updated.get(conversationId);
        if (conversation) {
          conversation.messages = [...conversation.messages, aiMessage];
          updated.set(conversationId, conversation);
        }
        return updated;
      });
    } finally {
      setIsAnalyzing(false);
    }
  }, [currentConversationId, startNewConversation]);

  // Clear conversation
  const clearConversation = useCallback(() => {
    if (currentConversationId) {
      setConversations(prev => {
        const updated = new Map(prev);
        updated.delete(currentConversationId);
        return updated;
      });
    }
    setCurrentConversationId(null);
  }, [currentConversationId]);

  const value = {
    conversations,
    currentConversation,
    currentConversationId,
    isTyping,
    isRecording,
    isAnalyzing,
    startNewConversation,
    sendMessage,
    sendVoiceMessage,
    analyzeImage,
    clearConversation,
    setCurrentConversationId
  };

  return (
    <AIChatContext.Provider value={value}>
      {children}
    </AIChatContext.Provider>
  );
};

// Mock AI response generator
const generateMockAIResponse = (userInput, context) => {
  const input = userInput.toLowerCase();
  
  // Destination suggestions
  if (input.includes('paris')) {
    return {
      text: "🗼 Paris is an amazing choice! The City of Light offers incredible art, cuisine, and romance. I can help you plan a perfect Paris itinerary.\n\nWhen are you planning to visit? How many days do you have?",
      suggested_actions: [
        'Plan a 5-day Paris trip',
        'Best time to visit Paris',
        'Paris on a budget',
        'Romantic Paris experiences'
      ]
    };
  }
  
  if (input.includes('beach') || input.includes('ocean') || input.includes('sea')) {
    return {
      text: "🏖️ Beach destinations are perfect for relaxation! Here are some amazing options:\n\n• **Maldives** - Crystal clear waters and overwater villas\n• **Bali** - Tropical paradise with culture\n• **Santorini** - Greek island beauty\n• **Hawaii** - Volcanic beaches and adventure\n\nWhat type of beach experience interests you most?",
      suggested_actions: [
        'Tropical paradise trip',
        'Greek islands adventure',
        'Hawaii vacation plan',
        'Budget beach destinations'
      ]
    };
  }
  
  if (input.includes('adventure') || input.includes('hiking') || input.includes('mountain')) {
    return {
      text: "⛰️ Adventure awaits! Here are some thrilling destinations:\n\n• **Nepal** - Himalayan trekking and culture\n• **New Zealand** - Extreme sports paradise\n• **Costa Rica** - Rainforests and wildlife\n• **Iceland** - Glaciers and volcanic landscapes\n\nWhat kind of adventure activities do you enjoy?",
      suggested_actions: [
        'Mountain trekking trip',
        'Adventure sports vacation',
        'Wildlife safari planning',
        'Extreme sports destinations'
      ]
    };
  }
  
  if (input.includes('budget') || input.includes('cheap') || input.includes('affordable')) {
    return {
      text: "💰 Budget travel can be incredibly rewarding! Here are some affordable gems:\n\n• **Vietnam** - Amazing food and culture\n• **Portugal** - European charm at great prices\n• **Mexico** - Rich culture and beautiful beaches\n• **Eastern Europe** - Historic cities and low costs\n\nWhat's your approximate budget range?",
      suggested_actions: [
        'Under $1000 trip ideas',
        'Budget Europe backpacking',
        'Affordable Asian destinations',
        'Local travel experiences'
      ]
    };
  }
  
  // Default response
  return {
    text: "That's interesting! I'd love to help you plan something amazing. Could you tell me more about:\n\n• What type of experience you're looking for?\n• Your preferred destinations or regions?\n• Your budget range?\n• How long you'd like to travel?\n\nThe more details you share, the better I can personalize your perfect trip! ✨",
    suggested_actions: [
      'I want relaxation',
      'Adventure and excitement',
      'Cultural experiences',
      'Food and wine tours'
    ]
  };
};
