package com.example.dohai90.carmasking;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.PorterDuff;
import android.graphics.PorterDuffXfermode;
import android.graphics.Rect;
import android.util.Log;

public class ImageUtils {

    private final static String TAG = "ImageUtils";
    public static Bitmap resizingBitmap(Bitmap origin, int resizedWidth, int resizedHeight) {
        if (origin == null) {
            Log.e(TAG, "resizingBitmap: original image is null");
            return null;
        }

        Bitmap resizedBitmap = Bitmap.createBitmap(resizedWidth, resizedHeight, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(resizedBitmap);
        canvas.drawBitmap(origin,
                new Rect(0, 0, origin.getWidth(), origin.getHeight()),
                new Rect(0, 0, resizedWidth, resizedHeight),
                null);

        return resizedBitmap;
    }

    public static Bitmap croppingBitmapWithMask(Bitmap resizedOrigin, Bitmap mask) {
        if (resizedOrigin == null || mask == null) {
            Log.e(TAG, "croppingBitmapWithMask: bitmap is null");
            return null;
        }

        final int w = resizedOrigin.getWidth();
        final int h = resizedOrigin.getHeight();
        if(w <=0 || h <= 0) {
            Log.e(TAG, "croppingBitmapWithMask: invalid input image size");
            return null;
        }

        Bitmap cropped = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(cropped);

        Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        paint.setXfermode(new PorterDuffXfermode(PorterDuff.Mode.SRC_ATOP));

        canvas.drawBitmap(resizedOrigin, 0, 0, null);
        canvas.drawBitmap(mask, 0, 0, paint);
        paint.setXfermode(null);

        return cropped;
    }
}
