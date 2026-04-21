type SearchBarProps = {
  value: string;
  onChange: (value: string) => void;
};

export function SearchBar({ value, onChange }: SearchBarProps) {
  return (
    <label className="search-wrap" htmlFor="listing-search">
      <span className="search-label">Search books</span>
      <input
        id="listing-search"
        type="search"
        className="search-input"
        placeholder="Search by title or description"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}
