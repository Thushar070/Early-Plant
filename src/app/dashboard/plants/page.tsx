'use client';

import { useState, useMemo } from 'react';
import { getPlants } from '@/services/plantService';
import { PlantCard } from '@/components/PlantCard';
import { PlantStatus } from '@/types/plant';
import { Leaf, Search, Frown } from 'lucide-react';

type FilterTab = 'all' | PlantStatus;

export default function PlantsPage() {
  const allPlants = getPlants();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<FilterTab>('all');

  const filteredPlants = useMemo(() => {
    return allPlants.filter((plant) => {
      const matchesSearch =
        search === '' ||
        plant.name.toLowerCase().includes(search.toLowerCase()) ||
        plant.location.toLowerCase().includes(search.toLowerCase());
      const matchesFilter = filter === 'all' || plant.status === filter;
      return matchesSearch && matchesFilter;
    });
  }, [allPlants, search, filter]);

  const tabs: { key: FilterTab; label: string }[] = [
    { key: 'all', label: 'All' },
    { key: 'healthy', label: 'Healthy' },
    { key: 'stressed', label: 'Stressed' },
    { key: 'critical', label: 'Critical' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-sage-100 flex items-center justify-center">
          <Leaf className="w-5 h-5 text-sage-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-sage-800">My Plants</h1>
          <p className="text-sage-500 text-sm">{allPlants.length} plants monitored</p>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-sage-400" />
        <input
          type="text"
          placeholder="Search plants by name or location..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 bg-white border border-sage-200 rounded-lg text-sage-800 placeholder:text-sage-400 focus:outline-none focus:ring-2 focus:ring-sage-300 focus:border-sage-300 text-sm"
        />
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filter === tab.key
                ? 'bg-sage-600 text-white'
                : 'bg-white border border-sage-200 text-sage-600 hover:bg-sage-50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Plants Grid */}
      {filteredPlants.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredPlants.map((plant) => (
            <PlantCard key={plant.id} plant={plant} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <Frown className="w-12 h-12 text-sage-300 mx-auto mb-3" />
          <p className="text-sage-500 font-medium">No plants found</p>
          <p className="text-sage-400 text-sm mt-1">Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  );
}
