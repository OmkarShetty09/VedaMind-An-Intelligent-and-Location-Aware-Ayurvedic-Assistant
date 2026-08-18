import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import { loadRoutine, regenerate } from "../store/dinacharyaSlice.js";

export function useDinacharya() {
  const dispatch = useDispatch();
  const { routine, status, error } = useSelector((s) => s.dinacharya);

  useEffect(() => {
    if (status === "idle") dispatch(loadRoutine());
  }, [dispatch, status]);

  return {
    routine,
    status,
    error,
    regenerate: () => dispatch(regenerate()),
  };
}
