import type { MoodOption } from "../../constants/moods";
import { MOOD_OPTIONS } from "../../constants/moods";
import "./MoodSelector.css";

interface MoodSelectorProps {
  onSelect: (mood: MoodOption) => void;
  disabled: boolean;
}

export default function MoodSelector({ onSelect, disabled }: MoodSelectorProps) {
  return (
    <div
      className="mood-selector"
      role="group"
      aria-label="Select your mood"
    >
      {MOOD_OPTIONS.map((option) => (
        <button
          key={option.value}
          className="mood-selector__option"
          onClick={() => onSelect(option)}
          disabled={disabled}
          aria-label={`${option.label} ${option.emoji}`}
          type="button"
        >
          <span className="mood-selector__emoji">{option.emoji}</span>
          <span className="mood-selector__label">{option.label}</span>
        </button>
      ))}
    </div>
  );
}
