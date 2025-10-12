import { useState } from "react";
import {
  PayPalButtons,
  PayPalButtonsComponentProps,
} from "@paypal/react-paypal-js";
import { useTranslation } from "react-i18next";
import { Spinner } from "@heroui/spinner";

import { paymentService } from "../../services/payment.service";

interface PaymentButtonProps {
  courseId: string;
  amount: number;
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export function PaymentButton({
  courseId,
  amount,
  onSuccess,
  onError,
}: PaymentButtonProps) {
  const { t } = useTranslation();
  const [isProcessing, setIsProcessing] = useState(false);

  const createOrder: PayPalButtonsComponentProps["createOrder"] = async () => {
    try {
      setIsProcessing(true);
      const data = await paymentService.createOrder(courseId);

      return data.order_id;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to create order";

      onError?.(message);
      throw error;
    } finally {
      setIsProcessing(false);
    }
  };

  const onApprove: PayPalButtonsComponentProps["onApprove"] = async (data) => {
    try {
      setIsProcessing(true);
      const result = await paymentService.captureOrder(data.orderID);

      if (result.success) {
        onSuccess?.();
      } else {
        onError?.("Payment capture failed");
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to process payment";

      onError?.(message);
    } finally {
      setIsProcessing(false);
    }
  };

  const onCancel: PayPalButtonsComponentProps["onCancel"] = () => {
    setIsProcessing(false);
    onError?.("Payment cancelled");
  };

  const onErrorHandler: PayPalButtonsComponentProps["onError"] = (err) => {
    setIsProcessing(false);
    const message =
      err instanceof Error ? err.message : "Payment error occurred";

    onError?.(message);
  };

  return (
    <div className="w-full">
      {isProcessing && (
        <div className="flex justify-center items-center py-4">
          <Spinner label={t("common.processing")} />
        </div>
      )}
      <PayPalButtons
        createOrder={createOrder}
        disabled={isProcessing}
        style={{
          layout: "vertical",
          color: "gold",
          shape: "rect",
          label: "paypal",
        }}
        onApprove={onApprove}
        onCancel={onCancel}
        onError={onErrorHandler}
      />
    </div>
  );
}
