interface CategoryTabsProps {
  selectedCategory: string
  onSelectCategory: (category: string) => void
}

const CATEGORIES = ['All Jobs', 'AI', 'Engineering']

export default function CategoryTabs({ selectedCategory, onSelectCategory }: CategoryTabsProps) {
  return (
    <>
      {CATEGORIES.map((category) => (
        <button
          key={category}
          onClick={() => onSelectCategory(category)}
          className={`px-4 sm:px-6 py-3 rounded-lg font-semibold transition-colors whitespace-nowrap text-sm sm:text-base ${
            selectedCategory === category
              ? 'bg-primary text-white'
              : 'bg-gray-900 text-gray-300 hover:bg-gray-800 border border-gray-800'
          }`}
          aria-label={`Filter by ${category}`}
          aria-pressed={selectedCategory === category}
        >
          {category}
        </button>
      ))}
    </>
  )
}
