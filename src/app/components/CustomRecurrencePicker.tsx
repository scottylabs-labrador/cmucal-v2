import {
  Box,
  Button,
  Checkbox,
  FormControl,
  FormControlLabel,
  FormLabel,
  InputLabel,
  MenuItem,
  Radio,
  RadioGroup,
  Select,
  SelectChangeEvent,
  TextField,
  Typography,
} from "@mui/material";
import { DatePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import dayjs, { Dayjs } from "dayjs";
import { useState } from "react";

const weekdays = ["S", "M", "T", "W", "T", "F", "S"];

interface CustomRecurrencePickerProps {
    
    show?: boolean;
    setShowUploadModalTwo: React.Dispatch<React.SetStateAction<boolean>>;
    onClose?: () => void;
}

export default function CustomRecurrencePicker({ show, onClose }: CustomRecurrencePickerProps) {
  const [interval, setInterval] = useState(1);
  const [frequency, setFrequency] = useState("week");
  const [selectedDays, setSelectedDays] = useState<number[]>([1, 2, 3, 4, 5]); // M-F
  const [ends, setEnds] = useState("never");
  const [endDate, setEndDate] = useState<Dayjs | null>(null);
  const [occurrences, setOccurrences] = useState(13);

  const toggleDay = (index: number) => {
    setSelectedDays((prev) =>
      prev.includes(index)
        ? prev.filter((d) => d !== index)
        : [...prev, index]
    );
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box display="flex" flexDirection="column" gap={2} maxWidth={300}>
        <Box display="flex" alignItems="center" gap={1}>
          <Typography>Repeat every</Typography>
          <TextField
            type="number"
            size="small"
            value={interval}
            onChange={(e) => setInterval(Number(e.target.value))}
            inputProps={{ min: 1 }}
            style={{ width: 60 }}
          />
          <FormControl size="small">
            <Select
              value={frequency}
              onChange={(e: SelectChangeEvent) =>
                setFrequency(e.target.value)
              }
            >
              <MenuItem value="day">day</MenuItem>
              <MenuItem value="week">week</MenuItem>
              <MenuItem value="month">month</MenuItem>
              <MenuItem value="year">year</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {frequency === "week" && (
          <Box display="flex" justifyContent="space-between">
            {weekdays.map((label, i) => (
              <Checkbox
                key={i}
                checked={selectedDays.includes(i)}
                onChange={() => toggleDay(i)}
                icon={<Box>{label}</Box>}
                checkedIcon={<Box fontWeight="bold">{label}</Box>}
              />
            ))}
          </Box>
        )}

        <FormControl>
          <FormLabel>Ends</FormLabel>
          <RadioGroup
            value={ends}
            onChange={(e) => setEnds(e.target.value)}
          >
            <FormControlLabel value="never" control={<Radio />} label="Never" />
            <FormControlLabel
              value="on"
              control={<Radio />}
              label={
                <DatePicker
                  label=""
                  value={endDate}
                  onChange={(newDate: Dayjs | null) => setEndDate(newDate)}
                  disabled={ends !== "on"}
                  slotProps={{
                    textField: { size: "small", disabled: ends !== "on" },
                  }}
                />
              }
            />
            <FormControlLabel
              value="after"
              control={<Radio />}
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  <TextField
                    type="number"
                    value={occurrences}
                    size="small"
                    disabled={ends !== "after"}
                    onChange={(e) => setOccurrences(Number(e.target.value))}
                    inputProps={{ min: 1 }}
                  />
                  <Typography>occurrences</Typography>
                </Box>
              }
            />
          </RadioGroup>
        </FormControl>

        <Box display="flex" justifyContent="space-between" mt={2}>
          <Button color="inherit">Cancel</Button>
          <Button variant="contained">Done</Button>
        </Box>
      </Box>
    </LocalizationProvider>
  );
}
