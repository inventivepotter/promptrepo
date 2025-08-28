'use client';

import React from 'react';
import {
  HStack,
  Button,
  Text,
} from '@chakra-ui/react';
import { LuChevronLeft, LuChevronRight } from 'react-icons/lu';
import { useColorModeValue } from '../../../components/ui/color-mode';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  totalItems: number;
  itemsPerPage: number;
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  totalItems,
  itemsPerPage,
}: PaginationProps) {
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const activeBg = useColorModeValue('blue.50', 'blue.900');
  const activeColor = useColorModeValue('blue.600', 'blue.300');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');

  if (totalPages <= 1) return null;

  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  const getPageNumbers = () => {
    const pages = [];
    const showPages = 5; // Show 5 page numbers at most
    
    let startPage = Math.max(1, currentPage - Math.floor(showPages / 2));
    const endPage = Math.min(totalPages, startPage + showPages - 1);
    
    // Adjust if we're near the end
    if (endPage - startPage + 1 < showPages) {
      startPage = Math.max(1, endPage - showPages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    
    return pages;
  };

  return (
    <HStack justify="space-between" align="center" mt={6} flexWrap="wrap" gap={4}>
      <Text fontSize="sm" color={mutedTextColor}>
        Showing {startItem}-{endItem} of {totalItems} results
      </Text>
      
      <HStack gap={1}>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          _hover={{ bg: hoverBg }}
        >
          <LuChevronLeft size={16} />
        </Button>
        
        {getPageNumbers().map((pageNum) => (
          <Button
            key={pageNum}
            size="sm"
            variant={currentPage === pageNum ? 'solid' : 'ghost'}
            onClick={() => onPageChange(pageNum)}
            bg={currentPage === pageNum ? activeBg : 'transparent'}
            color={currentPage === pageNum ? activeColor : mutedTextColor}
            _hover={{ bg: currentPage === pageNum ? activeBg : hoverBg }}
            minW={8}
          >
            {pageNum}
          </Button>
        ))}
        
        <Button
          size="sm"
          variant="ghost"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          _hover={{ bg: hoverBg }}
        >
          <LuChevronRight size={16} />
        </Button>
      </HStack>
    </HStack>
  );
}