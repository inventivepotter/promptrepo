'use client';

import React, { useState, useEffect } from 'react';
import { pricingService } from '@/services/llm/pricing/pricingService';
import { CostCalculation, TokenUsage } from '@/types/Pricing';

interface CostDisplayProps {
  modelName: string;
  tokenUsage: TokenUsage;
  className?: string;
  showDetails?: boolean;
}

export default function CostDisplay({ 
  modelName, 
  tokenUsage, 
  className = '',
  showDetails = false 
}: CostDisplayProps) {
  const [costCalculation, setCostCalculation] = useState<CostCalculation | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    calculateCost();
  }, [modelName, tokenUsage]);

  const calculateCost = async () => {
    setLoading(true);
    try {
      await pricingService.getPricingData();
      const calculation = pricingService.calculateCost(modelName, tokenUsage);
      setCostCalculation(calculation);
    } catch (error) {
      console.warn('Failed to calculate cost:', error);
      setCostCalculation(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={`inline-flex items-center space-x-1 ${className}`}>
        <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-gray-400"></div>
        <span className="text-xs text-gray-500">Calculating...</span>
      </div>
    );
  }

  if (!costCalculation) {
    return (
      <div className={`text-xs text-gray-400 ${className}`}>
        Cost unavailable
      </div>
    );
  }

  if (showDetails) {
    return (
      <div className={`text-xs space-y-1 ${className}`}>
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Input:</span>
          <span className="font-mono text-gray-800">
            {tokenUsage.inputTokens.toLocaleString()} tokens • {pricingService.formatCost(costCalculation.inputCost)}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Output:</span>
          <span className="font-mono text-gray-800">
            {tokenUsage.outputTokens.toLocaleString()} tokens • {pricingService.formatCost(costCalculation.outputCost)}
          </span>
        </div>
        {tokenUsage.reasoningTokens && tokenUsage.reasoningTokens > 0 && (
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Reasoning:</span>
            <span className="font-mono text-gray-800">
              {tokenUsage.reasoningTokens.toLocaleString()} tokens
            </span>
          </div>
        )}
        <div className="flex justify-between items-center pt-1 border-t border-gray-200">
          <span className="font-medium text-gray-700">Total:</span>
          <span className="font-mono font-bold text-gray-900">
            {pricingService.formatCost(costCalculation.totalCost)}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className={`inline-flex items-center space-x-1 text-xs ${className}`}>
      <span className="text-gray-500">Cost:</span>
      <span className="font-mono text-gray-700">{pricingService.formatCost(costCalculation.totalCost)}</span>
      <span className="text-gray-400">({costCalculation.provider})</span>
    </div>
  );
}